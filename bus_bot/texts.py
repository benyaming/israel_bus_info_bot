# messages
start_command = 'Hi! Send me location or a stop number!'
help_command = 'Send me your location, and I will find all public transport stops, located near to you. Or ' \
               'just write me your stop\'s number, and I will send you ' \
               'arrival times of nearest buses. The message with times will ' \
               'updating each few seconds for 15 minutes or until you send ' \
               'another number or will press "Stop tracking" button.\n\n' \
               'Author: @benyomin\n' \
               'Code: https://github.com/benyaming/israel_bus_info_bot'
incorrect_message = 'Text is incorrect, send station number!'
invalid_station = 'This stop code is not exists in the system!'
api_not_responding = 'The source of transport data is unavailable for the moment. Please, try again later.'
unknown_exception = 'Looks like an error occurred... The Bot\'s developer already working on it...'
no_stops_found = 'There are no stops found, try to send more accurate location!'
cancel = 'Canceled.'


# Keyboards
cancel_updating_button = '🛑 Stop updating'
add_to_saved_button = '🔖 Add to saved stops'
remove_from_saved_button = '❌ Remove'
done_button = 'Done'
cancel_button = 'Cancel'

# Callback alerts
cancel_updating_alert = 'Will stop soon.'
stop_deleted_ok_alert = 'Stop was successfully deleted from your saved stops.'

# Saved stops
rename_saved_stop = 'Write your stop name here or press "Done" for save default name.'
stop_saved = 'Stop "{}" successfully saved. Check it out with /my_stops command.'
here_is_your_stops = 'Here are your saved stops:'
saved_stops_emply_list = 'You have not saved any stop yet.'
stop_already_saved = 'This stop has already been saved.'
