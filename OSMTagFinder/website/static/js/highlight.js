/*

highlight v3  !! Modified by Jon Raasch (http://jonraasch.com) to fix IE6 bug !!

Highlights arbitrary terms.

<http://johannburkard.de/blog/programming/javascript/highlight-javascript-text-higlighting-jquery-plugin.html>

MIT license.

Johann Burkard
<http://johannburkard.de>
<mailto:jb@eaio.com>

*/

function highlight(node, pat, isTag) {
    pat = pat.toUpperCase()
    var skip = 0;
    if (node.nodeType == 3) {
        var pos = node.data.toUpperCase().indexOf(pat);
        if (pos >= 0) {
            var spannode = document.createElement('span');
            if (isTag === true)  {
                spannode.className = 'highlight-tag';
            }
            else {
                spannode.className = 'highlight-text';
            }

            var middlebit = node.splitText(pos);
            var endbit = middlebit.splitText(pat.length);
            var middleclone = middlebit.cloneNode(true);
            spannode.appendChild(middleclone);
            middlebit.parentNode.replaceChild(spannode, middlebit);
            skip = 1;
        }
    } else if (node.nodeType == 1 && node.childNodes && !/(script|style)/i.test(node.tagName)) {
        for (var i = 0; i < node.childNodes.length; ++i) {
            i += highlight(node.childNodes[i], pat, isTag);
        }
    }
    return skip;
}

function removeHighlight() {
    function newNormalize(node) {
        for (var i = 0, children = node.childNodes, nodeCount = children.length; i < nodeCount; i++) {
            var child = children[i];
            if (child.nodeType == 1) {
                newNormalize(child);
                continue;
            }
            if (child.nodeType != 3) {
                continue;
            }
            var next = child.nextSibling;
            if (next == null || next.nodeType != 3) {
                continue;
            }
            var combined_text = child.nodeValue + next.nodeValue;
            new_node = node.ownerDocument.createTextNode(combined_text);
            node.insertBefore(new_node, child);
            node.removeChild(child);
            node.removeChild(next);
            i--;
            nodeCount--;
        }
    }

    return this.find('span.highlight-tag, highlight-text').each(function() {
                var thisParent = this.parentNode;
                thisParent.replaceChild(this.firstChild, this);
                newNormalize(thisParent);
           }).end();


};