import 'package:flutter/foundation.dart';

import '../models/fund.dart';
import '../models/user_persona.dart';
import '../services/api_service.dart';

class RecommendationProvider extends ChangeNotifier {
  final ApiService _apiService;

  List<Fund> _recommendations = [];
  bool _isLoading = false;
  String? _error;
  UserPersona? _lastPersona;

  RecommendationProvider({ApiService? apiService})
      : _apiService = apiService ?? ApiService();

  List<Fund> get recommendations => _recommendations;
  bool get isLoading => _isLoading;
  String? get error => _error;
  UserPersona? get lastPersona => _lastPersona;
  bool get hasResults => _recommendations.isNotEmpty;

  Future<void> fetchRecommendations(UserPersona persona) async {
    _isLoading = true;
    _error = null;
    _lastPersona = persona;
    notifyListeners();

    try {
      _recommendations = await _apiService.getRecommendations(persona);
      _error = null;
    } on ApiException catch (e) {
      _error = e.message;
      _recommendations = [];
    } catch (e) {
      _error = 'Something went wrong. Please try again.';
      _recommendations = [];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> retry() async {
    if (_lastPersona != null) {
      await fetchRecommendations(_lastPersona!);
    }
  }

  void clear() {
    _recommendations = [];
    _error = null;
    _isLoading = false;
    _lastPersona = null;
    notifyListeners();
  }
}
