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



    // code for playlist page
    $(document).on('submit', '#playlist_form', function(e){
        e.preventDefault();
        // var old_video_area = $('#playlist_result_area_id').text()
        $('#playlist_result_area_id').text('');
        $('#single_single_video_id').html('');
        $.ajax({
            type: 'POST',
            url: '',
            data: {
                playlist_link_name: $('#playlist_link_id').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            async: true,
            success: function(data){
                var json_data = JSON.parse(JSON.stringify(data));
                // console.log(Object.keys(json_data.allVideoList).length)
                var new_video_area_text = "";
                var new_single_single_video_html = "<table class='w-100'><col width='70'><col width='100'><col width=''><col width='80'><tr><th>Sl No</th><th>Thumbnail</th><th>Title</th><th>Download</th></tr>"
                for (i = 0; i < Object.keys(json_data.allVideoList).length; i++) {
                    new_video_area_text += $('#playlist_result_area_id').text()
                    $.ajax({
                        type: 'GET',
                        url: 'http://127.0.0.1:8000/playlist-ajax',
                        data: {
                            video_no: i,
                            video_quality: $('#playlist_quality_id :selected').val(),
                            prefix: $('#prefix_id').is(':checked'),
                            reduce: $('#reduce_id').is(':checked'),
                            video_link: Object.values(json_data.allVideoList)[i]
                        },
                        async: true,
                        success: function(data){
                            var ajax_json_data = JSON.parse(JSON.stringify(data));
                            new_video_area_text += ajax_json_data['video_download_url'] + "\n"; 
                            new_single_single_video_html += "<tr><td>" + ajax_json_data['video_number'].toString() + "</td><td><img class='img-fluid thumbnail py-2' src='" + ajax_json_data['video_thumbnail'] + "' alt='Thumbnail'></td><td>" + ajax_json_data['video_title'] + "</td><td><a href='" + ajax_json_data['video_download_url'] + "'><button class='download-button'>Download</button></a></td></tr>";
                            $('#playlist_result_area_id').text(new_video_area_text);
                            $('#single_single_video_id').html(new_single_single_video_html);
                        }
                    });                  
                }
            } 
        });
    });


    // code for single page
    const single_form = document.getElementById('single_form');
    $(document).on('submit', '#single_form', function (e) {
        e.preventDefault();
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