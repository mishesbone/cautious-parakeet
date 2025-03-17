$(document).ready(function () {
    // Function to load content and mark the active link
    function loadContent(contentUrl) {
        $.get(contentUrl, function (data) {
            $('#content').html(data);
        });
    }

    // Event handling for link clicks
    $('.navigation ul li a').click(function (e) {
        e.preventDefault();
        var contentUrl = $(this).data('content-url');
        loadContent(contentUrl);
    });

    // Initial content load (e.g., dashboard)
    var initialContentUrl = $('#dashboardLink').data('content-url');
    loadContent(initialContentUrl);
});