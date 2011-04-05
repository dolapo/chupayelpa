goog.provide('minivishnu.chupayelpa.TodoSyncer');
goog.provide('minivishnu.chupayelpa.TodoSyncer.EventType');
goog.provide('minivishnu.chupayelpa.TodoSyncer.VenuesMatchFailedEvent');

goog.require('goog.Uri');
goog.require('goog.events.EventTarget');
goog.require('goog.net.XhrIo');

/**
 * @param {Array.<Object>} yelpBookmarks
 * @constructor
 * @extends {goog.events.EventTarget}
 */
minivishnu.chupayelpa.TodoSyncer = function(userId, yelpBookmarks) {
  goog.base(this);
  this.userId_ = userId;
  this.yelpBookmarks_ = yelpBookmarks;
};
goog.inherits(minivishnu.chupayelpa.TodoSyncer, goog.events.EventTarget);

minivishnu.chupayelpa.TodoSyncer.CHUNK_SIZE = 10;

minivishnu.chupayelpa.TodoSyncer.prototype.startMatching = function() {
  var cs = minivishnu.chupayelpa.TodoSyncer.CHUNK_SIZE;
  for (var i = 0; i < this.yelpBookmarks_.length; i += cs) {
    var chunk = goog.array.slice(this.yelpBookmarks_,
                                 i, Math.min(this.yelpBookmarks_.length, i + cs))
    var uri = new goog.Uri('/matchvenues');
    uri.getQueryData().add('user', this.userId_);
    uri.getQueryData().add('venues', goog.json.serialize(chunk));
    goog.net.XhrIo.send(uri, goog.bind(this.onBookmarksMatch_, this, chunk), 'GET',
                        undefined, undefined, 10000);
  }
};

/**
 * @private
 */
minivishnu.chupayelpa.TodoSyncer.prototype.onBookmarksMatch_ = function(bookmarks, e) {
  var xhr = e.target;
  if (xhr.getStatus() != 200) {
    this.dispatchEvent(
      new minivishnu.chupayelpa.TodoSyncer.VenuesMatchFailedEvent(bookmarks))
  } else {
    var obj = xhr.getResponseJson();
  }
};

minivishnu.chupayelpa.TodoSyncer.EventType = {
  VENUES_MATCHED: 'venuesmatched',
  VENUES_MATCH_FAILED: 'venuesmatchfailed'
};

/**
 * @constructor
 * @extends {goog.events.Event}
 */
minivishnu.chupayelpa.TodoSyncer.VenuesMatchFailedEvent = function(bookmarks) {
  goog.base(this, minivishnu.chupayelpa.TodoSyncer.EventType.VENUES_MATCH_FAILED);
  this.bookmarks = bookmarks;
};
goog.inherits(minivishnu.chupayelpa.TodoSyncer.VenuesMatchFailedEvent, goog.events.Event);
