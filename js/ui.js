goog.provide('minivishnu.chupayelpa.ui.BookmarksTable');

goog.require('goog.dom.classes');
goog.require('goog.ui.Component');
goog.require('minivishnu.chupayelpa.TodoSyncer');
goog.require('minivishnu.chupayelpa.TodoSyncer.VenuesMatchFailedEvent');
goog.require('minivishnu.chupayelpa.TodoSyncer.VenuesMatchedEvent');


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
  this.totalMatchedCount_ = 0;
  this.totalMatchedCountNode_ = this.getDomHelper().getElement('total-matched');
};
goog.inherits(minivishnu.chupayelpa.ui.BookmarksTable, goog.ui.Component);

minivishnu.chupayelpa.ui.BookmarksTable.prototype.decorateInternal = function(element) {
  goog.base(this, 'decorateInternal', element);
};

/**
 * @private
 */
minivishnu.chupayelpa.ui.BookmarksTable.prototype.onVenuesMatched_ = function(ev) {
  var dh = this.getDomHelper();
  for (var yelpId in ev.venuesByYelpId) {
    var venues = ev.venuesByYelpId[yelpId];
    if (venues.length > 0) {
      var venue = venues[0];

      var node = dh.getElement(yelpId);
      if (!node) continue;
      // TODO(dolapo): just use soy
      var successNode = dh.getElementsByTagNameAndClass('div', 'success', node)[0];

      var link = dh.getElementsByTagNameAndClass('a', 'link', successNode)[0];
      link.setAttribute('href', 'http://foursquare.com/venue/' + venue['id'])
      dh.setTextContent(link, venue['name']);

      var otherMatches = dh.getElementsByTagNameAndClass('span', 'other-matches', node)[0];
      if (venues.length == 1) {
        goog.dom.removeNode(otherMatches);
      } else {
        var otherCount = dh.getElementsByTagNameAndClass('span', 'other-count', otherMatches)[0];
        dh.setTextContent(otherCount, venues.length - 1);
      }
      this.totalMatchedCount_++;
      dh.setTextContent(this.totalMatchedCountNode_, this.totalMatchedCount_);
    }
    goog.dom.classes.swap(node, 'loading', 'success');
  }
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
