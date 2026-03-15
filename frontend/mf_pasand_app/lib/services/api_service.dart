import 'dart:convert';
import 'dart:io' show Platform;

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;

import '../models/fund.dart';
import '../models/user_persona.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, {this.statusCode});

  @override
  String toString() => 'ApiException: $message (status: $statusCode)';
}

class ApiService {
  static String get baseUrl {
    if (kIsWeb) return 'http://localhost:8000';
    try {
      if (Platform.isAndroid) return 'http://192.168.1.7:8000';
    } catch (_) {}
    return 'http://localhost:8000';
  }

  final http.Client _client;

  ApiService({http.Client? client}) : _client = client ?? http.Client();

  Future<List<Fund>> getRecommendations(UserPersona persona) async {
    try {
      final response = await _client
          .post(
            Uri.parse('$baseUrl/recommend'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(persona.toJson()),
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        List<dynamic> fundsList;
        if (data is List) {
          fundsList = data;
        } else if (data is Map && data.containsKey('recommendations')) {
          fundsList = data['recommendations'] as List;
        } else if (data is Map && data.containsKey('funds')) {
          fundsList = data['funds'] as List;
        } else {
          throw ApiException('Unexpected response format');
        }
        return fundsList
            .map((json) => Fund.fromJson(json as Map<String, dynamic>))
            .toList();
      } else {
        final body = jsonDecode(response.body);
        final detail = body is Map ? (body['detail'] ?? body['message']) : null;
        throw ApiException(
          detail?.toString() ?? 'Failed to get recommendations',
          statusCode: response.statusCode,
        );
      }
    } on ApiException {
      rethrow;
    } catch (e) {
      if (e.toString().contains('Connection refused') ||
          e.toString().contains('SocketException') ||
          e.toString().contains('TimeoutException')) {
        throw ApiException(
          'Unable to connect to server. Please check if the backend is running.',
        );
      }
      throw ApiException('An unexpected error occurred: ${e.toString()}');
    }
  }

  Future<List<Fund>> getFunds({String? category, int page = 1}) async {
    try {
      final queryParams = <String, String>{
        'page': page.toString(),
      };
      if (category != null && category.isNotEmpty) {
        queryParams['category'] = category;
      }

      final uri =
          Uri.parse('$baseUrl/funds').replace(queryParameters: queryParams);
      final response =
          await _client.get(uri).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        List<dynamic> fundsList;
        if (data is List) {
          fundsList = data;
        } else if (data is Map && data.containsKey('funds')) {
          fundsList = data['funds'] as List;
        } else {
          fundsList = [];
        }
        return fundsList
            .map((json) => Fund.fromJson(json as Map<String, dynamic>))
            .toList();
      } else {
        throw ApiException(
          'Failed to fetch funds',
          statusCode: response.statusCode,
        );
      }
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException('Failed to fetch funds: ${e.toString()}');
    }
  }

  Future<Fund> getFundDetail(String schemeCode) async {
    try {
      final response = await _client
          .get(Uri.parse('$baseUrl/funds/$schemeCode'))
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return Fund.fromJson(data as Map<String, dynamic>);
      } else {
        throw ApiException(
          'Fund not found',
          statusCode: response.statusCode,
        );
      }
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException('Failed to fetch fund details: ${e.toString()}');
    }
  }

  Future<bool> checkHealth() async {
    try {
      final response = await _client
          .get(Uri.parse('$baseUrl/health'))
          .timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  void dispose() {
    _client.close();
  }
}
