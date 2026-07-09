import api from './api';
import type { PageLink } from '../types';

export const getPages = async (): Promise<PageLink[]> => {
  const { data } = await api.get<PageLink[]>('/pages');
  return data;
};
