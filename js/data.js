goog.provide('minivishnu.chupayelpa.TodoSyncer');
goog.provide('minivishnu.chupayelpa.TodoSyncer.EventType');

goog.require('goog.events.EventTarget');
goog.require('goog.net.XhrIo');

/**
 * @param {Array.<Object>} yelpBookmarks
 * @constructor
 * @extends {goog.events.EventTarget}
 */
minivishnu.chupayelpa.TodoSyncer = function(yelpBookmarks) {
  goog.base(this);
  this.yelpBookmarks_ = yelpBookmarks;
};
goog.inherits(minivishnu.chupayelpa.TodoSyncer, goog.events.EventTarget);

minivishnu.chupayelpa.TodoSyncer.prototype.startMatching = function() {
  // TODO(dolapo): really dumb to post this big document back to the ui, but whateves
};

minivishnu.chupayelpa.TodoSyncer.EventType = {
  VENUES_MATCHED: 'venuesmatched'
}
