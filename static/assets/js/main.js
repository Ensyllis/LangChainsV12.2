/*
	Spectral by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

(function($) {

	var	$window = $(window),
		$body = $('body'),
		$wrapper = $('#page-wrapper'),
		$banner = $('#banner'),
		$header = $('#header');

	// Breakpoints.
		breakpoints({
			xlarge:   [ '1281px',  '1680px' ],
			large:    [ '981px',   '1280px' ],
			medium:   [ '737px',   '980px'  ],
			small:    [ '481px',   '736px'  ],
			xsmall:   [ null,      '480px'  ]
		});

	// Play initial animations on page load.
		$window.on('load', function() {
			window.setTimeout(function() {
				$body.removeClass('is-preload');
			}, 100);
		});

	// Mobile?
		if (browser.mobile)
			$body.addClass('is-mobile');
		else {

			breakpoints.on('>medium', function() {
				$body.removeClass('is-mobile');
			});

			breakpoints.on('<=medium', function() {
				$body.addClass('is-mobile');
			});

		}

	// Scrolly.
		$('.scrolly')
			.scrolly({
				speed: 1500,
				offset: $header.outerHeight()
			});

	// Menu.
		$('#menu')
			.append('<a href="#menu" class="close"></a>')
			.appendTo($body)
			.panel({
				delay: 500,
				hideOnClick: true,
				hideOnSwipe: true,
				resetScroll: true,
				resetForms: true,
				side: 'right',
				target: $body,
				visibleClass: 'is-menu-visible'
			});

	// Header.
		if ($banner.length > 0
		&&	$header.hasClass('alt')) {

			$window.on('resize', function() { $window.trigger('scroll'); });

			$banner.scrollex({
				bottom:		$header.outerHeight() + 1,
				terminate:	function() { $header.removeClass('alt'); },
				enter:		function() { $header.addClass('alt'); },
				leave:		function() { $header.removeClass('alt'); }
			});

		}

})(jQuery);



(function() {

    // Vars.
        var $form = document.querySelectorAll('#signup-form')[0],
            $submit = document.querySelectorAll('#signup-form input[type="submit"]')[0],
            $message;

    // Bail if addEventListener isn't supported.
        if (!('addEventListener' in $form))
            return;

    // Message.
        $message = document.createElement('span');
            $message.classList.add('message');
            $form.appendChild($message);

        $message._show = function(type, text) {

            $message.innerHTML = text;
            $message.classList.add(type);
            $message.classList.add('visible');
        };

        $message._hide = function() {
            $message.classList.remove('visible');
        };

    // Events.
        $form.addEventListener('submit', function(event) {

            event.stopPropagation();
            event.preventDefault();

            // Hide message.
                $message._hide();

            // Disable submit.
                $submit.disabled = true;

            // Get the prompt value from the form
            var promptValue = document.getElementById('prompt').value;

            // Send the prompt value to the /query endpoint using fetch
            fetch('/soteriology_query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt: promptValue })
            })
            .then(response => response.json())
            .then(data => {
                // Enable submit.
                $submit.disabled = false;

                // Reset form.
                $form.reset();

                // Show result and source documents.
				if (data.error) {
				    $message._show('failure', 'Error: ' + data.error);
				} else {
				    let messageContent = 'Result: ' + data.result;
				    $message._show('success', messageContent);
				
				    const documentsContainer = document.getElementById('documentsContainer');
				    documentsContainer.innerHTML = ''; // Clear previous content
				
				    if (data.source_documents && data.source_documents.length > 0) {
				        data.source_documents.forEach((doc, index) => {
				            // Create button
				            const button = document.createElement('button');
				            button.textContent = `Source ${index + 1}`;
				            button.id = `toggleButton${index}`;
						
				            // Create collapsible container
				            const collapseContainer = document.createElement('div');
				            collapseContainer.id = `documentContainer${index}`;
				            collapseContainer.classList.add('collapse');
						
				            // Set the content of the collapsible container
				            collapseContainer.innerHTML = doc;
						
				            // Append button and collapsible container to the documentsContainer
				            documentsContainer.appendChild(button);
				            documentsContainer.appendChild(collapseContainer);
						
				            // Add event listener to the button to toggle the visibility of the container
				            button.addEventListener('click', function() {
				                collapseContainer.classList.toggle('show');
				            });
				        });
				    }
				}

        	})
            .catch(error => {
                // Enable submit.
                $submit.disabled = false;

                // Show error message.
                $message._show('failure', 'Error: ' + error.message);
            });
        });
	})();

