import securescaffold
import securescaffold.views


app = securescaffold.create_app(__name__)

# The only route redirects visitors to /intl/LANG/ depending on the
# Accept-Language header.
app.add_url_rule("/", "lang_redirect", securescaffold.views.lang_redirect)
app.config["LOCALES"] = ["en", "fr"]
app.config["LOCALES_REDIRECT_TO"] = "/intl/{locale}/"
