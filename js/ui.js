goog.provide('minivishnu.chupayelpa.ui.BookmarksTable');

goog.require('minivishnu.chupayelpa.TodoSyncer');
goog.require('goog.ui.Component');


/**
 * @param {minivishnu.chupayelpa.TodoSyncer} syncer
 * @constructor
 * @extends {goog.ui.Component}
 */
minivishnu.chupayelpa.ui.BookmarksTable = function(syncer, opt_domHelper) {
  goog.base(this, opt_domHelper);
  this.syncer_ = syncer;
  this.getHandler().listen(this.syncer_,
                           minivishnu.chupayelpa.TodoSyncer.EventType.VENUES_MATCHED,
                           this.onInitialSync_);
};
goog.inherits(minivishnu.chupayelpa.ui.BookmarksTable, goog.ui.Component);

minivishnu.chupayelpa.ui.BookmarksTable.prototype.decorateInternal = function(element) {
  goog.base(this, 'decorateInternal', element);
};

/**
 * @private
 */
minivishnu.chupayelpa.ui.BookmarksTable.prototype.onInitialSync_ = function(ev) {
};
