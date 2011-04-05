goog.provide('minivishnu.chupayelpa.TodoSyncer');
goog.provide('minivishnu.chupayelpa.TodoSyncer.EventType');
goog.provide('minivishnu.chupayelpa.TodoSyncer.VenuesMatchFailedEvent');
goog.provide('minivishnu.chupayelpa.TodoSyncer.VenuesMatchedEvent');

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

minivishnu.chupayelpa.TodoSyncer.CHUNK_SIZE = 5;

minivishnu.chupayelpa.TodoSyncer.prototype.startMatching = function() {
  this.requestBatch_(0);
};

minivishnu.chupayelpa.TodoSyncer.prototype.requestBatch_ = function(start) {
  var cs = minivishnu.chupayelpa.TodoSyncer.CHUNK_SIZE;
  if (start > this.yelpBookmarks_.length) return;
  var chunk = goog.array.slice(this.yelpBookmarks_,
                               start, Math.min(this.yelpBookmarks_.length, start + cs))
  var uri = new goog.Uri('/matchvenues');
  uri.getQueryData().add('user', this.userId_);
  uri.getQueryData().add('bookmarks', goog.json.serialize(chunk));
  goog.net.XhrIo.send(uri, goog.bind(this.onBookmarksMatch_, this, chunk, start + cs), 'GET',
                      undefined, undefined, 30000);
}

/**
 * @private
 */
minivishnu.chupayelpa.TodoSyncer.prototype.onBookmarksMatch_ =
    function(bookmarks, nextBatchStart, e) {
  var xhr = e.target;
  if (xhr.getStatus() != 200) {
    this.dispatchEvent(
      new minivishnu.chupayelpa.TodoSyncer.VenuesMatchFailedEvent(bookmarks))
  } else {
    var obj = xhr.getResponseJson();
    this.dispatchEvent(
      new minivishnu.chupayelpa.TodoSyncer.VenuesMatchedEvent(obj['results']))
    // TODO(dolapo): uncomment when done testing.
    this.requestBatch_(nextBatchStart);
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

/**
 * @constructor
 * @extends {goog.events.Event}
 */
minivishnu.chupayelpa.TodoSyncer.VenuesMatchedEvent = function(venuesByYelpId) {
  goog.base(this, minivishnu.chupayelpa.TodoSyncer.EventType.VENUES_MATCHED);
  this.venuesByYelpId = venuesByYelpId;
}
goog.inherits(minivishnu.chupayelpa.TodoSyncer.VenuesMatchedEvent, goog.events.Event);
