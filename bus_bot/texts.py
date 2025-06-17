# messages
start_command = 'Hi! Send me your location or a stop number!'
help_command = 'Send me your location, and I will find all public transport stops located near you. Or ' \
               'just write your stop number, and I will send you ' \
               'arrival times for the nearest buses. The message with times will ' \
               'update every few seconds for 15 minutes or until you send ' \
               'another number or press the "Stop tracking" button.\n\n' \
               'Supported vehicles: buses, trains, and light rail.\n' \
               'Map color legend:\n' \
               '🔴 - Bus stop\n' \
               '🟢 - Bus station with multiple platforms\n' \
               '🟣 - Gush Dan light rail stop\n' \
               '🟠 - Jerusalem light rail stop\n' \
               '🔵 - Railway station\n\n' \
               '<a href="https://t.me/benyamin_stuff">News and other bots |</a>' \
               '<a href="https://t.me/benyomin">Author |</a>' \
               '<a href="https://github.com/benyaming/israel_bus_info_bot">Source code</a>'
incorrect_message = 'The text is incorrect, please send a station number!'
invalid_station = 'This stop code does not exist in the system!'
api_not_responding = 'The source of transport data is unavailable at the moment. Please try again later.'
unknown_exception = 'It looks like an error occurred... The bot\'s developer is already working on it...'
no_stops_found = 'No stops found, try sending a more accurate location!'
cancel = 'Canceled.'

# Keyboards
cancel_updating_button = '🛑 Stop updating'
add_to_saved_button = '🔖 Add to saved stops'
remove_from_saved_button = '❌ Remove'
done_button = 'Done'
cancel_button = 'Cancel'
restart_stop_updating_button = '🔄 Restart updating'

# Callback alerts
cancel_updating_alert = 'Will stop soon.'
stop_deleted_ok_alert = 'Stop was successfully deleted from your saved stops.'

# Saved stops
rename_saved_stop = 'Write your stop name here or press "Done" to save the default name.'
stop_saved = 'Stop "{}" successfully saved. Check it out with the /my_stops command.'
here_is_your_stops = 'Here are your saved stops:'
saved_stops_emply_list = 'You have not saved any stops yet.'
stop_already_saved = 'This stop has already been saved.'
