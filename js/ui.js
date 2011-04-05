goog.provide('minivishnu.chupayelpa.ui.BookmarksTable');

goog.require('goog.dom.classes');
goog.require('goog.ui.Component');
goog.require('minivishnu.chupayelpa.TodoSyncer');
goog.require('minivishnu.chupayelpa.TodoSyncer.VenuesMatchFailedEvent');


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
                           this.onVenuesMatched_);
  this.getHandler().listen(this.syncer_,
                           minivishnu.chupayelpa.TodoSyncer.EventType.VENUES_MATCH_FAILED,
                           this.onVenuesMatchFailed_);
};
goog.inherits(minivishnu.chupayelpa.ui.BookmarksTable, goog.ui.Component);

minivishnu.chupayelpa.ui.BookmarksTable.prototype.decorateInternal = function(element) {
  goog.base(this, 'decorateInternal', element);
};

/**
 * @private
 */
minivishnu.chupayelpa.ui.BookmarksTable.prototype.onVenuesMatched_ = function(ev) {
};

/**
 * @private
 */
minivishnu.chupayelpa.ui.BookmarksTable.prototype.onVenuesMatchFailed_ = function(ev) {
  var bookmarks = ev.bookmarks;
  for (var i = 0, bookmark; bookmark = ev.bookmarks[i]; i++) {
    var node = this.getDomHelper().getElement(bookmark['id']);
    goog.dom.classes.swap(node, 'loading', 'failed');
  }
};
