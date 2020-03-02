$(document).ready(function () {
    // page preloader code here
    // const page_pre_loader = document.getElementById("page_pre_loader");

    // $("#playlist_submit_button").click(function () {
    // const playlist_link_input = document.getElementById("playlist_list")
    // console.log(playlist_link_input.value)
    // var dataValue = playlist_link_input.value
    // page_pre_loader.classList.remove("d-none");
    // $.get("",
    // {
    //     playlist_link_name : playlist_link_input.value
    // },
    // function(data, status){
    //   alert("Data: " + data + "\nStatus: " + status);
    // });
    // $("#playlist-input-container" ).fadeOut("slow", function() {
    //     // Animation complete
    // });
    // });
    // $(window).bind("pageshow", function(event) {
    //     if (event.originalEvent.persisted) {
    //         window.location.reload();
    //     }
    // });





    // code for single page TESTING
    const single_form = document.getElementById('single_form');
    $(document).on('submit', '#single_form', function (e) {
        e.preventDefault()
        $.ajax({
            type: 'POST',
            url: '',
            data: {
                single_video_input: $('#single_video_input').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (data) {
                var json_data = JSON.parse(JSON.stringify(data));
                $('#single_video_thumbnail_id').html('<img src="' + json_data.thumbnail + '" class="img-fluid" alt="thumbnail">');
                $('#single_video_title_id').text(json_data.title);
                $('#single_video_time_id').html(json_data.time);
                var streams = "";
                // var output = Object.keys(json_data.streams)[1];
                for (i = 0; i < Object.keys(data.streams).length; i++) {
                    streams += "<a href='" + Object.values(json_data.streams)[i] + "'><button>" + Object.keys(json_data.streams)[i] + "</button>";
                }
                $('#single_video_download_id').html(streams);
            }
        });
    });

});