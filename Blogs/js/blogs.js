/**
 * 列表方式显示日志列表
 */
 API.Blogs.showList = function() {
    // 统一按发布时间降序，避免数据文件插入顺序影响展示
    blogs.sort((a, b) => (b.pubTime || '').localeCompare(a.pubTime || ''));

    // 日志分类清单
    const categoryMaps = API.Utils.groupedByField(blogs, 'category');

    // 基于模板渲染列表
    const list_html = template(TPL.BLOGS_TYPE_LIST, { blogs: blogs, categoryMaps: categoryMaps });

    // 渲染
    $('#blogs-list').html(list_html);
}

/**
 * 表格方式显示日志列表
 */
API.Blogs.showTableList = function() {
    // 初始化日志表格
    API.Utils.initTable("blogs-table", [{
        checkbox: true,
        clickToSelect: true,
        width: "50"
    }, {
        field: 'title',
        title: '标题',
        align: 'left',
        width: "30",
        widthUnit: "%",
        sortable: true,
        formatter: (value, row) => {
            return '<a href="info.html?blogId={0}" >{1}</a> '.format(row.blogid || row.blogId, value);
        }
    }, {
        field: 'category',
        title: '分类',
        align: 'center',
        width: "150",
        sortable: true
    }, {
        field: 'rt_uin',
        title: '类型',
        align: 'center',
        width: "50",
        sortable: true,
        formatter: (value, row, index, field) => {
            return API.Blogs.getBlogLabel(row).join(',');
        }
    }, {
        field: 'pubTime',
        title: '发布时间',
        align: 'center',
        width: "150",
        sortable: true,
        formatter: (value) => {
            return API.Utils.formatDate(value);
        }
    }, {
        field: 'replynum',
        title: '评论数',
        align: 'center',
        width: "20",
        sortable: true
    }, {
        field: 'custom_visitor.viewCount',
        title: '阅读数',
        align: 'center',
        width: "20",
        sortable: true
    }], blogs.slice().sort((a, b) => (b.pubTime || '').localeCompare(a.pubTime || '')));
}

$(function() {

    // 显示日志列表
    switch (QZone_Config.Blogs.showType) {
        case '0':
            // 表格方式展示
            API.Blogs.showTableList();
            break;
        default:
            // HTML方式展示
            API.Blogs.showList();
            break;
    }
});