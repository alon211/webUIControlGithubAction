/**
 * 主 JavaScript 文件
 */

$(document).ready(function() {
    console.log('应用已加载');

    // 初始化 Bootstrap 提示
    $('[data-bs-toggle="tooltip"]').tooltip();

    // 初始化 Bootstrap 弹出框
    $('[data-bs-toggle="popover"]').popover();
});

/**
 * 显示提示消息
 */
function showAlert(message, type) {
    type = type || 'info';
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    const container = $('#alert-container');
    container.html(alertHtml);

    // 3秒后自动关闭
    setTimeout(() => {
        container.find('.alert').alert('close');
    }, 3000);
}

/**
 * 显示加载状态
 */
function showLoading(button) {
    const $btn = $(button);
    $btn.prop('disabled', true);
    $btn.data('original-text', $btn.html());
    $btn.html('<span class="spinner-border spinner-border-sm me-2"></span>加载中...');
}

/**
 * 隐藏加载状态
 */
function hideLoading(button) {
    const $btn = $(button);
    $btn.prop('disabled', false);
    $btn.html($btn.data('original-text'));
}

/**
 * 格式化日期时间
 */
function formatDateTime(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN');
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
