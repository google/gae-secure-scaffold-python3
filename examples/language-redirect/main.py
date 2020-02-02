import securescaffold
import securescaffold.views


app = securescaffold.create_app(__name__)
app.add_url_rule("/", "lang_redirect", securescaffold.views.lang_redirect)
app.config["LOCALES"] = ["en"]
app.config["LOCALES_REDIRECT_TO"] = "/intl/{locale}/"
