$(function() {
    let blogId = API.Utils.getUrlParam('blogId');

    // Get metadata from blogs_meta.js
    const blogIndex = blogs.getIndex(blogId * 1, 'blogid');
    const meta = blogs[blogIndex];

    // Render title/time/author from metadata (instant, no waiting)
    document.title = 'QQ空间备份-' + (meta.custom_title || meta.title);
    $("#blog_title").text(meta.custom_title || meta.title);
    $("#blog_time").text(API.Utils.formatDate(meta.lastModifyTime || meta.pubtime));
    if (meta.custom_author) {
        $("#blog_author").text("作者：" + meta.custom_author).show();
    }

    // Lazy-load full blog content
    const script = document.createElement('script');
    script.src = 'json/blogs/blog_' + blogId + '.js';
    script.onload = function() {
        const blog = window.blogDetail;

        // Render content
        const $blogHtml = $('<div><div>').html(API.Utils.base64ToUtf8(blog.custom_html));
        $('#blog_content').html($blogHtml.html());

        // Render comments
        const comments_tpl = document.getElementById('comments_tpl').innerHTML;
        const comments_html = template(comments_tpl, { blog: blog });
        $("#comments_html").html(comments_html);

        // Image gallery
        $('#blog_content img').on('click', function() {
            const $galleryDom = $('#blog_content').get(0);
            const imgIdx = $(this).attr('data-idx');

            if ($galleryDom.galleryIns) {
                $galleryDom.galleryIns.openGallery(imgIdx * 1);
                return;
            }

            const galleryIns = lightGallery($galleryDom, {
                plugins: [lgZoom, lgFullscreen, lgThumbnail, lgRotate],
                mode: 'lg-fade',
                selector: '.lightgallery',
                download: false,
                thumbnail: true,
                loop: false
            });
            $galleryDom.galleryIns = galleryIns;
            galleryIns.openGallery(imgIdx * 1);
        });

        // Like & visitors (use full blog data)
        API.Common.registerShowVisitorsWin([blog]);
        API.Common.registerShowLikeWin([blog]);
    };
    script.onerror = function() {
        $('#blog_content').html('<div class="alert alert-warning">文章内容加载失败</div>');
    };
    document.head.appendChild(script);
});
