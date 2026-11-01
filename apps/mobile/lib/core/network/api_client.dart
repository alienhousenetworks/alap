import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiClient {
  ApiClient(this.storage)
      : dio = Dio(BaseOptions(
          baseUrl: const String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8000') + '/api/v1',
          connectTimeout: const Duration(seconds: 12),
          receiveTimeout: const Duration(seconds: 50),
          sendTimeout: const Duration(seconds: 20),
          headers: {'Accept': 'application/json'},
        )) {
    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await storage.read(key: 'access_token');
        if (token != null) options.headers['Authorization'] = 'Bearer $token';
        handler.next(options);
      },
      onError: (error, handler) async {
        final path = error.requestOptions.path;
        final isAuthRoute = path.contains('/auth/login') || path.contains('/auth/register') || path.contains('/auth/refresh');
        if (error.response?.statusCode != 401 || isAuthRoute || error.requestOptions.extra['retried'] == true) {
          return handler.next(error);
        }
        try {
          await _refreshSession();
          final token = await storage.read(key: 'access_token');
          final options = error.requestOptions;
          options.headers['Authorization'] = 'Bearer $token';
          options.extra['retried'] = true;
          handler.resolve(await dio.fetch(options));
        } catch (_) {
          await storage.delete(key: 'access_token');
          await storage.delete(key: 'refresh_token');
          handler.next(error);
        }
      },
    ));
  }

  final FlutterSecureStorage storage;
  final Dio dio;
  Future<void>? _refreshing;

  Future<void> _refreshSession() async {
    if (_refreshing != null) return _refreshing!;
    final completer = Completer<void>();
    _refreshing = completer.future;
    try {
      final refreshToken = await storage.read(key: 'refresh_token');
      if (refreshToken == null) throw StateError('No refresh token');
      final response = await Dio().post(
        dio.options.baseUrl + '/auth/refresh',
        data: {'refresh_token': refreshToken},
        options: Options(sendTimeout: const Duration(seconds: 12), receiveTimeout: const Duration(seconds: 12)),
      );
      await storage.write(key: 'access_token', value: response.data['access_token'] as String);
      await storage.write(key: 'refresh_token', value: response.data['refresh_token'] as String);
      completer.complete();
    } catch (error, stack) {
      completer.completeError(error, stack);
      rethrow;
    } finally {
      _refreshing = null;
    }
  }
}
