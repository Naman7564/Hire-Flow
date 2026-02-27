/* ============================================
   Interview Detail Page — Interactions
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {
    initInterviewCopyButtons();
});

/**
 * Copy-to-clipboard for the meeting link button
 */
function initInterviewCopyButtons() {
    document.querySelectorAll('.btn-copy[data-link]').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            var link = this.getAttribute('data-link');
            if (!link) return;

            var button = this;
            var originalHTML = button.innerHTML;

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(link)
                    .then(function () { showCopiedState(button, originalHTML); })
                    .catch(function () { fallbackCopy(link, button, originalHTML); });
            } else {
                fallbackCopy(link, button, originalHTML);
            }
        });
    });
}

function fallbackCopy(text, button, originalHTML) {
    var textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();

    try {
        document.execCommand('copy');
        showCopiedState(button, originalHTML);
    } catch (err) {
        showToast('Failed to copy link.', 'error');
    }

    document.body.removeChild(textarea);
}

function showCopiedState(button, originalHTML) {
    button.classList.add('copied');
    button.innerHTML = '<i class="fas fa-check"></i> Copied!';

    // Toast feedback
    if (typeof showToast === 'function') {
        showToast('Meeting link copied to clipboard!', 'success');
    }

    setTimeout(function () {
        button.classList.remove('copied');
        button.innerHTML = originalHTML;
    }, 2500);
}
