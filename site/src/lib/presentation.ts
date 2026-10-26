export const grades = ['S', 'A', 'B', 'C'] as const;
export type Grade = typeof grades[number];
export interface EventRecord {
  id: string; event_date: string; title: string; summary: string; category: string;
  subcategory: string; impact: Grade; impact_reason: string; orgs: string[];
  verified: 'official' | 'confirmed' | 'rumor'; models?: string[]; status?: string;
  sources: { url: string; publisher: string; type: string }[];
  impact_history?: { at: string; from: string; to: string; reason: string }[];
  [key: string]: unknown;
}
export const credibility = { official: '官方', confirmed: '媒体证实', rumor: '传闻' };
export const statusLabels: Record<string, string> = {
  announced: '已发布公告', preview: '预览/测试', rolling_out: '逐步推送中',
  ga: '全面可用', completed: '已完成', withdrawn: '已撤回', ongoing: '进行中',
};
export function statusLabel(s?: string): string | undefined {
  return s ? (Object.prototype.hasOwnProperty.call(statusLabels, s) ? statusLabels[s] : s) : undefined;
}
export const sourceTypes: Record<string, string> = { official: '官方', media: '媒体', community: '社区' };
export function monday(date: string): string {
  const value = new Date(date.slice(0, 10) + 'T00:00:00Z');
  value.setUTCDate(value.getUTCDate() - (value.getUTCDay() + 6) % 7);
  return value.toISOString().slice(0, 10);
}
export interface ChartData { categories: string[]; weeks: string[]; distribution: number[][]; trend: number[][]; heatRows: string[]; heat: number[][] }
