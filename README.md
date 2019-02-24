# 301remover

A service to resolve shortened URLs encountered in the browser.

# why?

Because URL shortening was a fucking awful idea.

## link rot

When a shortener dies all the shortened links become inaccessible. This is a source of link rot and URL shorteners are especially difficult to archive.

The [URLTeam](http://urlte.am) project has done great work on backing up URL shortener services by scanning them in bulk. However, this is a slow process and will probably never backup the entirety of large shorteners like `bit.ly` or `goo.gl`.

With a browser extension, we can make sure that we archive the shortened URLs that real people are likely to encounter on the internet.

301remover uses archived URLs from the URLTeam project to make dead links work again and archives all the URL shortener links that it encounters.

## privacy

Shortener services invade your privacy and make money by collecting analytics on your browsing habits.

301remover resolves links on a server running outside of your web browser, so bit.ly and other shorteners never see a request from you.

## performance

Shortener services harm performance by introducing unnecessary redirects.
301remover resolves links with a single bulk request as soon as the page loads. This means that the redirect is removed before you click on a link.

## security

Shorteners present a security and usability issue by obfuscating the destination of links.

301remover puts the real link address right into the webpage. Mousing over a link shows the real destination in the link hover status bar. Copying the link address gives you the real address too.
