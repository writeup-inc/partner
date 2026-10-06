
(() => {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.site-nav');
  const closeMenu = () => {if(toggle && nav){toggle.setAttribute('aria-expanded','false');nav.classList.remove('is-open');}};
  if(toggle && nav){
    toggle.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('is-open',open);});
    nav.addEventListener('click',e=>{if(e.target.closest('a'))closeMenu();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&toggle.getAttribute('aria-expanded')==='true'){closeMenu();toggle.focus();}});
    document.addEventListener('click',e=>{if(!e.target.closest('.site-header'))closeMenu();});
    window.matchMedia('(min-width:1021px)').addEventListener('change',closeMenu);
  }
  document.querySelectorAll('[data-copy]').forEach(button=>{
    button.addEventListener('click',async()=>{
      const block=document.getElementById(button.dataset.copy);const status=button.parentElement.querySelector('.copy-status');
      try{await navigator.clipboard.writeText(block.innerText);status.textContent='コピーしました。送る前に相手に合わせて編集してください。';}
      catch{const selection=window.getSelection();const range=document.createRange();range.selectNodeContents(block);selection.removeAllRanges();selection.addRange(range);status.textContent='文面を選択しました。コピーしてご利用ください。';}
    });
  });
})();
