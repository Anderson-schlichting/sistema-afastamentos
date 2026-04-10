let chart;
let dados={};

function m(v){return v.toLocaleString('pt-BR',{style:'currency',currency:'BRL'});}
function p(v){return Number(v.replace(/\./g,'').replace(',','.'))||0;}

// BUSCA CNPJ
document.getElementById('cnpj').addEventListener('blur', async function(){
let cnpj = this.value.replace(/\D/g,'');
if(cnpj.length !== 14) return;

try{
let r = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${cnpj}`);
let d = await r.json();

document.getElementById('empresa').value = d.razao_social || '';
document.getElementById('cnae').value = d.cnae_fiscal + " - " + (d.cnae_fiscal_descricao || '');
}catch{}
});

function calcular(){

let folha=p(document.getElementById('folha').value)||0;
let rat=(+document.getElementById('rat').value||0)/100;
let fap=(+document.getElementById('fapAtual').value)||0;

let b91=+document.getElementById('b91').value||0;
let b92=+document.getElementById('b92').value||0;
let b93=+document.getElementById('b93').value||0;
let b94=+document.getElementById('b94').value||0;
let cat=+document.getElementById('cat').value||0;

let total=b91+b92+b93+b94+cat;

// FAP ideal automático
let fapIdeal= total===0?0.5: total<=3?0.8: total<=8?1.0:1.2;

let atual=folha*rat*fap;
let correto=folha*rat*fapIdeal;
let diferenca=atual-correto;

// faixa recuperação
let recMin=diferenca*60;
let recMax=recMin*1.3;
let recMed=(recMin+recMax)/2;

// risco
let risco=(b92+b93)>0?"ALTO":(b91+cat)>5?"MÉDIO":"BAIXO";

dados={empresa:empresa.value,cnpj:cnpj.value,cnae:cnae.value,atual,correto,diferenca,recMin,recMax,recMed,risco,fapIdeal};

document.getElementById('resultado').innerHTML = `
<b>Custo atual:</b> ${m(atual)}<br>
<b>Custo correto:</b> ${m(correto)}<br>
<b>Diferença mensal:</b> ${m(diferenca)}<br><br>

<b>💰 Recuperação estimada (5 anos):</b><br>
De ${m(recMin)} até ${m(recMax)}<br>
Média: <b>${m(recMed)}</b><br><br>

<b>FAP ideal:</b> ${fapIdeal.toFixed(2)}<br>
<b>Risco:</b> ${risco}
`;

let anos=['1','2','3','4','5'];
let eco=[],gas=[];
for(let i=1;i<=5;i++){
eco.push(recMed/5*i);
gas.push(atual*12*i);
}

if(chart)chart.destroy();
chart=new Chart(grafico,{
type:'line',
data:{labels:anos,datasets:[
{label:'Recuperação média',data:eco},
{label:'Gasto acumulado',data:gas}
]}
});
}

function gerarPDF(){

html2canvas(document.getElementById('relatorio')).then(canvas=>{
let img=canvas.toDataURL('image/png');
let pdf=new jspdf.jsPDF('p','mm','a4');

let w=190;
let h=canvas.height*w/canvas.width;

pdf.addImage(img,'PNG',10,10,w,h);
pdf.save("Relatorio_FAP.pdf");
});
}
