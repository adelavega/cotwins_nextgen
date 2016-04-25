## Common functions

## Set up PsiTurk and preload the pages that will be shown after task is done
# dataHandler = PsiTurk(uniqueid, adServerLoc)

## Alternatively set this up for local server hosting using dataHandler.js

dataHandler = DataHandler(uniqueid, experimentname, sessionid, sid)

# Calculates the mean of a numeric array (for feedback)
mean = (numericArray) ->
	sum = numericArray.reduce((a, b) -> a + b)
	avg = sum / numericArray.length

	return avg

## Global session class
## Iterates through blocks and other events such as instructions
class Session
	constructor: (@blocks) ->
		@blockNumber = 0
		@max_blocks = @blocks.length
		@imgs_loaded = 0
		
	start: ->
		# This ensures that the images for the two buttons are loaded
		# Could probably be done better
		@imgs_loaded++
		if @imgs_loaded is 2
			@nextBlock()

	# Go to next block
	nextBlock: ->
		@currBlock = @blocks[@blockNumber]
		if @blockNumber >= @max_blocks
			@endSession()
		else
			@blockNumber++

			# Start the next block
			# When block ends, call exitBlock with argument
			# Argument is whether to continue or go back (instructions)
			$('.tasktext').html(' ')
			@currBlock.start ((arg1) => @exitBlock arg1)

	# Go back a block	
	prevBlock: ->
		if @blockNumber > 1
			@blockNumber = @blockNumber - 2

		@currBlock = @blocks[@blockNumber]

		@blockNumber++
		@currBlock.start ((arg1) => @exitBlock arg1)

	# This gets called when block is over.
	# Saves data and goes back or forward
	exitBlock: (next = true) ->
		dataHandler.saveData()
		if next
			@nextBlock()
		else
			@prevBlock()
	
	# Ends it all
	endSession: ->
		dataHandler.completeHIT()

	keyPress: (e) ->
		code = e.charCode || e.keyCode
		input = String.fromCharCode(code).toLowerCase()

		if input == "j"
			$('rightButton').click()
		
		@currBlock.keyPress input
		
	# Handles button clocks (mostly for questionnaires)
	buttonClick: (e) ->
		@currBlock.buttonClick(e)

# This class simply displays the post questionnaire and 
# collects information from it once button is clocked
class Questionnaire
	start: (@exitTrial) ->
		$('body').html(dataHandler.getPage('postquestionnaire.html'))

	buttonClick: ->

		any_blank = false
		$("select").each (i, val) ->
			if @value == "NONE"
				any_blank = true

		if any_blank
			console.log("Some blank")
			$("#noqs").removeClass("hidden")

		else
			$("select").each (i, val) ->
				dataHandler.recordUnstructuredData @id, @value

			dataHandler.recordUnstructuredData 'openended', $('#openended').val()
			dataHandler.saveData()
			@exitTrial()
		  


# Displays debriefing and when button is clicked ends
class Debriefing
	start: (@exitTrial) ->
		$('body').html(dataHandler.getPage(experimentname + '/debriefing.html'))

	buttonClick: ->
		@exitTrial()	


class FinishInstructions
	constructor: ->

	start: (@exitBlock) ->
		dataHandler.finishInstructions()
		@exitBlock()

@dataHandler = dataHandler

@common = {
	Questionnaire
	Debriefing
	FinishInstructions
	mean
	Session
}