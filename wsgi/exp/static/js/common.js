// Generated by CoffeeScript 1.9.3
(function() {
  var Debriefing, FinishInstructions, Session, dataHandler, mean;

  dataHandler = DataHandler(sessionid);

  mean = function(numericArray) {
    var avg, sum;
    sum = numericArray.reduce(function(a, b) {
      return a + b;
    });
    avg = sum / numericArray.length;
    return avg;
  };

  Session = (function() {
    function Session(blocks) {
      this.blocks = blocks;
      this.blockNumber = 0;
      this.max_blocks = this.blocks.length;
      this.imgs_loaded = 0;
    }

    Session.prototype.start = function() {
      this.imgs_loaded++;
      if (this.imgs_loaded === 2) {
        return this.nextBlock();
      }
    };

    Session.prototype.nextBlock = function() {
      this.currBlock = this.blocks[this.blockNumber];
      if (this.blockNumber >= this.max_blocks) {
        return this.endSession();
      } else {
        this.blockNumber++;
        $('.tasktext').html(' ');
        return this.currBlock.start(((function(_this) {
          return function(arg1) {
            return _this.exitBlock(arg1);
          };
        })(this)));
      }
    };

    Session.prototype.prevBlock = function() {
      if (this.blockNumber > 1) {
        this.blockNumber = this.blockNumber - 2;
      }
      this.currBlock = this.blocks[this.blockNumber];
      this.blockNumber++;
      return this.currBlock.start(((function(_this) {
        return function(arg1) {
          return _this.exitBlock(arg1);
        };
      })(this)));
    };

    Session.prototype.exitBlock = function(next) {
      if (next == null) {
        next = true;
      }
      dataHandler.saveData();
      if (next) {
        return this.nextBlock();
      } else {
        return this.prevBlock();
      }
    };

    Session.prototype.endSession = function() {
      dataHandler.completeTask();
      return dataHandler.exitTask();
    };

    Session.prototype.keyPress = function(e) {
      var code, input;
      code = e.charCode || e.keyCode;
      input = String.fromCharCode(code).toLowerCase();
      if (input === "j") {
        $('rightButton').click();
      }
      return this.currBlock.keyPress(input);
    };

    Session.prototype.buttonClick = function(e) {
      return this.currBlock.buttonClick(e);
    };

    return Session;

  })();

  Debriefing = (function() {
    function Debriefing() {}

    Debriefing.prototype.start = function(exitTrial) {
      this.exitTrial = exitTrial;
      return $('body').html(dataHandler.getPage(experimentname + '/debriefing.html'));
    };

    Debriefing.prototype.buttonClick = function() {
      return this.exitTrial();
    };

    return Debriefing;

  })();

  FinishInstructions = (function() {
    function FinishInstructions() {}

    FinishInstructions.prototype.start = function(exitBlock) {
      this.exitBlock = exitBlock;
      dataHandler.finishInstructions();
      return this.exitBlock();
    };

    return FinishInstructions;

  })();

  this.dataHandler = dataHandler;

  this.common = {
    Debriefing: Debriefing,
    FinishInstructions: FinishInstructions,
    mean: mean,
    Session: Session
  };

}).call(this);
