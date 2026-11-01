import '../../core/network/api_client.dart';

class MediaRepository {
  MediaRepository(this.api);
  final ApiClient api;
  Future<Map<String, dynamic>> image(String prompt, String conversationId) async =>
      Map<String, dynamic>.from((await api.dio.post('/media/images', data: {'prompt': prompt, 'conversation_id': conversationId})).data as Map);
  Future<Map<String, dynamic>> voice(String text, String conversationId) async =>
      Map<String, dynamic>.from((await api.dio.post('/media/voice', data: {'text': text, 'conversation_id': conversationId})).data as Map);
}
