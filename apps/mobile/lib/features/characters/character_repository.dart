import '../../core/network/api_client.dart';

class CharacterRepository {
  CharacterRepository(this.api);
  final ApiClient api;

  Future<List<Map<String, dynamic>>> discover() async {
    final response = await api.dio.get('/characters/discover');
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  Future<List<Map<String, dynamic>>> mine() async {
    final response = await api.dio.get('/characters/mine');
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  Future<Map<String, dynamic>> create({
    required String name, required String description, required String greeting,
    required Map<String, String> personality, required String visibility,
  }) async {
    final response = await api.dio.post('/characters', data: {
      'name': name, 'description': description, 'greeting': greeting,
      'personality': personality, 'visibility': visibility,
    });
    return Map<String, dynamic>.from(response.data as Map);
  }
}
