import { init, use, type EChartsCoreOption } from 'echarts/core';
import { HeatmapChart, LineChart, BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, VisualMapComponent, LegendComponent, AriaComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { grades, type ChartData } from './presentation';
use([HeatmapChart, LineChart, BarChart, GridComponent, TooltipComponent, VisualMapComponent, LegendComponent, AriaComponent, CanvasRenderer]);
export function renderCharts(data: ChartData) {
  const ids = ['distribution','trend','heatmap'];
  const charts = ids.map(id => { const el = document.getElementById(id)!; el.textContent = ''; return init(el); });
  function paint() {
    const css = getComputedStyle(document.documentElement);
    const token = (name: string) => css.getPropertyValue(name).trim();
    const text = token('--text-secondary');
    const axis = { axisLabel:{color:text}, axisLine:{lineStyle:{color:token('--border')}}, splitLine:{lineStyle:{color:token('--border')}} };
    const common = { animation:!matchMedia('(prefers-reduced-motion: reduce)').matches, textStyle:{color:text,fontFamily:css.fontFamily}, aria:{enabled:true}, tooltip:{confine:true,backgroundColor:token('--surface'),textStyle:{color:token('--text')},borderColor:token('--border')}, legend:{type:'scroll',bottom:0,textStyle:{color:text},pageTextStyle:{color:text},pageIconColor:text} };
    const options: EChartsCoreOption[] = [
      {...common,grid:{left:78,right:46,top:16,bottom:45},xAxis:{...axis,type:'value',minInterval:1},yAxis:{...axis,type:'category',data:data.categories,inverse:true},series:grades.map((grade,g)=>({name:`${grade} 级`,type:'bar',stack:'events',barMaxWidth:24,itemStyle:{color:token(`--grade-${grade}`)},data:data.distribution.map(row=>row[g]),label:{show:g===3,position:'right',color:text,formatter:(p:{dataIndex:number})=>`${data.distribution[p.dataIndex].reduce((a,b)=>a+b,0)} 条`}}))},
      {...common,color:data.categories.map((_,i)=>token(`--series-${i+1}`)),tooltip:{...common.tooltip,trigger:'axis'},grid:{left:42,right:20,top:26,bottom:60},xAxis:{...axis,type:'category',data:data.weeks.map(w=>w.slice(5))},yAxis:{...axis,type:'value',minInterval:1},series:data.categories.map((name,i)=>({name,type:'line',symbolSize:7,lineStyle:{width:2.5,type:i>3?'dashed':'solid'},data:data.trend[i]}))},
      {...common,grid:{left:220,right:20,top:15,bottom:80},xAxis:{...axis,type:'category',data:data.weeks.map(w=>w.slice(5))},yAxis:{...axis,type:'category',data:data.heatRows,inverse:true,axisLabel:{color:text,interval:0,fontSize:11}},visualMap:{min:0,max:Math.max(1,...data.heat.flat()),orient:'horizontal',left:'center',bottom:0,textStyle:{color:text},inRange:{color:[token('--heat-zero'),token('--heat-mid'),token('--heat-high')]}},series:[{type:'heatmap',data:data.heat.flatMap((row,y)=>row.map((n,x)=>[x,y,n])),itemStyle:{borderWidth:2,borderColor:token('--surface')},emphasis:{itemStyle:{borderColor:token('--text'),borderWidth:2}}}]},
    ];
    charts.forEach((chart,i)=>chart.setOption(options[i]));
  }
  paint();
  const resize = new ResizeObserver(()=>charts.forEach(chart=>chart.resize()));
  ids.forEach(id=>resize.observe(document.getElementById(id)!));
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change',paint);
  matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',paint);
}
