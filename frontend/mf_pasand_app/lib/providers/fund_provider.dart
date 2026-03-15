import 'package:flutter/foundation.dart';

import '../models/fund.dart';
import '../services/api_service.dart';

class FundProvider extends ChangeNotifier {
  final ApiService _apiService;

  List<Fund> _funds = [];
  Fund? _selectedFund;
  bool _isLoading = false;
  bool _isLoadingDetail = false;
  String? _error;
  String? _detailError;
  int _currentPage = 1;
  String? _currentCategory;
  bool _hasMore = true;

  FundProvider({ApiService? apiService})
      : _apiService = apiService ?? ApiService();

  List<Fund> get funds => _funds;
  Fund? get selectedFund => _selectedFund;
  bool get isLoading => _isLoading;
  bool get isLoadingDetail => _isLoadingDetail;
  String? get error => _error;
  String? get detailError => _detailError;
  bool get hasMore => _hasMore;

  Future<void> fetchFunds({String? category, bool refresh = false}) async {
    if (refresh) {
      _currentPage = 1;
      _funds = [];
      _hasMore = true;
    }

    _currentCategory = category;
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final newFunds =
          await _apiService.getFunds(category: category, page: _currentPage);
      if (newFunds.isEmpty) {
        _hasMore = false;
      } else {
        _funds.addAll(newFunds);
        _currentPage++;
      }
      _error = null;
    } on ApiException catch (e) {
      _error = e.message;
    } catch (e) {
      _error = 'Failed to load funds.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadMore() async {
    if (!_isLoading && _hasMore) {
      await fetchFunds(category: _currentCategory);
    }
  }

  Future<void> fetchFundDetail(String schemeCode) async {
    _isLoadingDetail = true;
    _detailError = null;
    notifyListeners();

    try {
      _selectedFund = await _apiService.getFundDetail(schemeCode);
      _detailError = null;
    } on ApiException catch (e) {
      _detailError = e.message;
    } catch (e) {
      _detailError = 'Failed to load fund details.';
    } finally {
      _isLoadingDetail = false;
      notifyListeners();
    }
  }

  void setSelectedFund(Fund fund) {
    _selectedFund = fund;
    notifyListeners();
  }

  void clearDetail() {
    _selectedFund = null;
    _detailError = null;
    notifyListeners();
  }
}
