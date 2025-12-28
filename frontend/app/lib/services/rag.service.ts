import { http } from '../api/http';
import { ENDPOINTS } from '../api/endpoints';

export async function askRag(question: string): Promise<string> {
  const res = await http.post(ENDPOINTS.RAG.QUERY, { question });
  const answer = res.data?.answer;

  if (!answer) {
    throw new Error('Réponse RAG invalide');
  }
  return answer;
}
