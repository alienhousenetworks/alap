import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../core/network/api_client.dart';

class AuthRepository {
  AuthRepository(this.api, this.storage);
  final ApiClient api;
  final FlutterSecureStorage storage;

  Future<void> login(String email, String password) async {
    final response = await api.dio.post('/auth/login', data: {'email': email, 'password': password});
    await _saveTokens(response.data);
  }

  Future<void> register(String email, String password, String displayName, bool confirmAdult) async {
    final response = await api.dio.post('/auth/register', data: {
      'email': email, 'password': password, 'display_name': displayName, 'confirm_adult': confirmAdult,
    });
    await _saveTokens(response.data);
  }

  Future<void> _saveTokens(dynamic data) async {
    await storage.write(key: 'access_token', value: data['access_token'] as String);
    await storage.write(key: 'refresh_token', value: data['refresh_token'] as String);
  }

  Future<void> logout() async {
    final refresh = await storage.read(key: 'refresh_token');
    if (refresh != null) {
      try { await api.dio.post('/auth/logout', data: {'refresh_token': refresh}); } catch (_) {}
    }
    await storage.delete(key: 'access_token');
    await storage.delete(key: 'refresh_token');
  }

  Future<bool> hasSession() async => await storage.read(key: 'access_token') != null;
}


  Future<void> deleteAccount(String password) async {
    await api.dio.delete('/auth/me', data: {'password': password});
    await storage.delete(key: 'access_token');
    await storage.delete(key: 'refresh_token');
  }

  Future<Map<String, dynamic>> exportData() async {
    final response = await api.dio.get('/auth/me/export');
    return Map<String, dynamic>.from(response.data as Map);
  }
