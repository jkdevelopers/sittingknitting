document.addEventListener('DOMContentLoaded', function () {
    $('[data-component]')
        .css({'border': '1px dashed red', 'cursor': 'pointer'})
        .attr('title', 'Click to edit')
        .tooltip({track: true})
        .click(function () {
            var id = $(this).attr('data-component');
            var url = '/edit/' + id;
            window.open(url, '_blank', 'height=400,width=400');
        });
});
