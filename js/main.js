goog.provide('minivishnu.chupayelpa.main');
goog.require('minivishnu.chupayelpa.TodoSyncer');
goog.require('minivishnu.chupayelpa.ui.BookmarksTable');

// not really a component. maybe should be. hack-a-thon!


/**
 * @param {Array.<Object>} yelpBookmarks
 */
minivishnu.chupayelpa.main = function(userId, yelpBookmarks) {
  window.setTimeout(function() {
    var table = goog.dom.getElement('bk-table');
    if (table) {
      var syncer = new minivishnu.chupayelpa.TodoSyncer(userId, yelpBookmarks);
      var ui = new minivishnu.chupayelpa.ui.BookmarksTable(syncer);
      ui.decorate(table);
      syncer.startMatching();
    }
  }, 1000);
};

goog.exportSymbol('minivishnu.chupayelpa.main', minivishnu.chupayelpa.main)
