import { init, use } from 'echarts/core';
import { HeatmapChart, LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, VisualMapComponent, LegendComponent, AriaComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
use([HeatmapChart, LineChart, GridComponent, TooltipComponent, VisualMapComponent, LegendComponent, AriaComponent, CanvasRenderer]);
export function renderCharts(page) {
  const cats = page.taxonomy.map(c => c.name);
  const data = cats.flatMap((c, y) => page.weeks.map((w, x) => [x, y, Object.values(page.agg.category_impact_week[c]?.[w] ?? {}).reduce((a:number,b:number) => a+b,0)]));
  const heat = init(document.querySelector('#heatmap')!);
  heat.setOption({ aria: {enabled:true}, tooltip: {position:'top'}, grid:{left:85,right:20,top:20,bottom:100}, xAxis:{type:'category',data:page.weeks,axisLabel:{rotate:35}},yAxis:{type:'category',data:cats},visualMap:{min:0,max:Math.max(1,...data.map(d=>d[2])),orient:'horizontal',left:'center',bottom:0,inRange:{color:['#edf4e9','#8ac5a4','#145942']}},series:[{type:'heatmap',data,label:{show:true}}] });
  const trend = init(document.querySelector('#trend')!);
  trend.setOption({aria:{enabled:true},tooltip:{trigger:'axis'},legend:{type:'scroll',bottom:0},grid:{left:45,right:20,top:25,bottom:100},xAxis:{type:'category',data:page.weeks,axisLabel:{rotate:35}},yAxis:{type:'value',name:'影响力指数'},series:cats.map(name=>({name,type:'line',data:page.agg.category_week_index[name],smooth:false}))});
  const resize = new ResizeObserver(() => {heat.resize();trend.resize();});
  resize.observe(document.querySelector('#heatmap')!);resize.observe(document.querySelector('#trend')!);
}
