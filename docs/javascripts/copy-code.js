document.addEventListener('DOMContentLoaded', () => {
  const blocks = document.querySelectorAll('pre > code');

  blocks.forEach((code) => {
    const pre = code.parentElement;
    if (!pre || pre.dataset.copyReady === 'true') return;

    pre.dataset.copyReady = 'true';
    pre.style.position = 'relative';

    const wrapper = document.createElement('div');
    wrapper.className = 'copy-code-wrapper';
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(pre);

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-code-button';
    button.setAttribute('aria-label', '复制代码');
    button.textContent = '复制';
    wrapper.appendChild(button);

    button.addEventListener('click', async () => {
      const text = code.innerText.replace(/\n$/, '');
      try {
        await navigator.clipboard.writeText(text);
        button.textContent = '已复制';
        button.classList.add('is-copied');
        setTimeout(() => {
          button.textContent = '复制';
          button.classList.remove('is-copied');
        }, 1800);
      } catch (error) {
        button.textContent = '复制失败';
        button.classList.add('is-error');
        setTimeout(() => {
          button.textContent = '复制';
          button.classList.remove('is-error');
        }, 1800);
      }
    });
  });
});
