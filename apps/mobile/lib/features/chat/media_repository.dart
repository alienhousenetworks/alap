import '../../core/network/api_client.dart';

class MediaRepository {
  MediaRepository(this.api);
  final ApiClient api;

  Future<Map<String, dynamic>> _withUrl(String path, Map<String, dynamic> data) async {
    final response = await api.dio.post(path, data: data);
    final asset = Map<String, dynamic>.from(response.data as Map);
    final link = await api.dio.get('/media/' + asset['id'].toString() + '/url');
    asset['url'] = link.data['url'] as String;
    return asset;
  }

  Future<Map<String, dynamic>> generateImage(String prompt) => _withUrl('/media/images', {'prompt': prompt});
  Future<Map<String, dynamic>> generateSpeech(String text, {String voice = 'alloy'}) => _withUrl('/media/speech', {'text': text, 'voice': voice});
}
