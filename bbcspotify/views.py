import webapp2
import jinja2
import os
import logging

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))


class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)


    def render_template(
        self,
        filename,
        template_values,
        **template_args
        ):
        template = jinja_environment.get_template(filename)
        self.response.out.write(template.render(template_values))


class MainPage(BaseHandler):
    def post(self):
        """
        after the url has been given, make the playlist...
        """
        url = self.request.get('url')
        title, playlist = self.get_playlist(url)
        self.render_template('show_playlist.html', {'title' : title, 'playlist' : playlist})


    def get(self):
        """
        show the form to submit a url
        """
        self.render_template('get_playlist_form.html', {})


    def get_playlist(self, url):
        """
        Make the playlist from the url
        """
        from spotify import BBC
        fetcher = BBC()
        title, playlist = fetcher.get_playlist(url)
        return title, playlist


class AboutPage(BaseHandler):

    def get(self):
        """
        Display the about page
        """
        logging.info('Test logging.')
        self.render_template('about.html', {})
