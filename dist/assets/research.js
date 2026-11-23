const toc=document.querySelector('.article-toc');
if(toc){const mobile=matchMedia('(max-width:760px)');const update=()=>{toc.open=!mobile.matches;};update();mobile.addEventListener('change',update);}
