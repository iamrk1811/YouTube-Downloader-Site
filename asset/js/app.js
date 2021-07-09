$(document).ready(function () {
    // Binding function if someone press back button (RELOAD)
    $(window).bind("pageshow", function(event) {
        if (event.originalEvent.persisted) {
            window.location.reload();
        }
    });

    var page_pre_loader = document.getElementById('page_pre_loader');

    var progress_no = 0;
    // code for playlist page
    $(document).on('submit', '#playlist_form', function(e){
        // Prevent default behavior of the form
        e.preventDefault();
        const progressBar = document.getElementById('prog');

        // Tasks that i have to perform before request to server
        $('#playlist_result_container_id').fadeOut('slow', function(){});
        $('#single_single_video_id').fadeOut('slow', function(){});
        $('#footer').fadeOut('slow', function(){});
        $('#single_video_table tbody').empty();
        $('#single_video_table').append('<tr><th>Sl No</th><th>Thumbnail</th><th>Title</th><th>Download</th></tr>');
        page_pre_loader.classList.remove('d-none');
        $('#playlist_result_area_id').text('');

        // Request to the Server
        $.ajax({
            type: 'POST',
            url: '',
            data: {
                playlist_link_name: $('#playlist_link_id').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            async: true,
            success: function(data){
                // Tasks that i have to perform before work with the data
                $('#playlist_result_container_id').fadeIn('slow', function(){});
                $('#single_single_video_id').fadeIn('slow', function(){});
                $('#footer').fadeIn('slow', function(){});
                page_pre_loader.classList.add('d-none');
                // Parsing JsonResponse to JSON Object
                var json_data = JSON.parse(JSON.stringify(data));

                // var number_of_videos = Object.keys(json_data.allVideoList).length;
                // Looping through all video list link 
                // And sending GET request to get download url, title, thumbnail
                for (i = 0; i < Object.keys(json_data.allVideoList).length; i++) {
                    $.ajax({
                        type: 'GET',
                        url: '/playlist-ajax',
                        data: {
                            video_no: i,
                            video_quality: $('#playlist_quality_id :selected').val(),
                            prefix: $('#prefix_id').is(':checked'),
                            reduce: $('#reduce_id').is(':checked'),
                            video_link: Object.values(json_data.allVideoList)[i]
                        },
                        async: true,
                        // Success function for single video output
                        success: function(data){
                            // Working with progress bar
                            progress_no += 1;
                            progress = Math.floor((progress_no/Object.keys(json_data.allVideoList).length) * 100);
                            progressBar.style.width = progress.toString() + "%";
                            // Parsing JsonResponse to JSON Object
                            var ajax_json_data = JSON.parse(JSON.stringify(data));
                            // Getting download url
                            download_url = ajax_json_data['video_download_url'] + "\n"; 
                            // Getting thumbnail, title, download url, video number
                            valid_download_url = ajax_json_data['video_download_url'] == "" ? "#" : ajax_json_data['video_download_url'];
                            single_video_html = "<tr><td>" + ajax_json_data['video_number'].toString() + "</td><td><img class='img-fluid thumbnail py-2' src='" + ajax_json_data['video_thumbnail'] + "' alt='Thumbnail'></td><td>" + ajax_json_data['video_title'] + "</td><td><a href='" + valid_download_url + "'><button class='download-button'>Download</button></a></td></tr>";
                            // Showing to front end
                            $('#single_video_table').append(single_video_html);
                            $('#playlist_result_area_id').append(download_url);                           
                        }
                    });                  
                }
                // Setting progress bar no to zero
                progress_no = 0;
            } 
        });
    });


    // code for single page
    const single_form = document.getElementById('single_form');
    $(document).on('submit', '#single_form', function (e) {
        // Prevent default behavior of the form
        e.preventDefault();
        // Tasks that i have to perform before sending request to the server
        $('#footer').fadeOut('slow', function(){});
        $("#single_result_container" ).fadeOut("slow", function(){});
        page_pre_loader.classList.remove("d-none");
        // Sending request to the server
        $.ajax({
            type: 'POST',
            url: '',
            data: {
                single_video_input: $('#single_video_input').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            // Success function
            success: function (data) { 
                // Parsing JsonResponse to JSON Object
                var json_data = JSON.parse(JSON.stringify(data));
                
                if (json_data.error != "") {
                    console.log("Error")
                } else {
                    // Showing content to front end
                    $('#single_video_thumbnail_id').html('<img src="' + json_data.thumbnail + '" class="img-fluid" alt="thumbnail">');
                    $('#single_video_title_id').text(json_data.title);
                    $('#single_video_time_id').html(json_data.time);
                    // Adding javascript code dynamically with html code
                    var streams = "<select id='single_download_select_id' onchange='optionChanged()'><script type='text/javascript'> function optionChanged(){$('#dynamicURL').attr('href', $('#single_download_select_id :selected').val());}</script>";
                    for (i = 0; i < Object.keys(data.streams).length; i++) {
                        streams += "<option value='" + Object.values(json_data.streams)[i] + "'>" + Object.keys(json_data.streams)[i] + "</option>";
                    }
                    streams += "</select><a id='dynamicURL' href=''><button class='single-download-button'>Download</button></a>"
                    $('#single_video_download_id').html(streams);
                    $('#dynamicURL').attr('href', Object.values(json_data.streams)[0]); 
                }
                // End Task
                page_pre_loader.classList.add('d-none');
                $("#single_result_container" ).fadeIn("slow", function(){});
                $('#footer').fadeIn('slow', function(){});
            }
        });
    });
    
});