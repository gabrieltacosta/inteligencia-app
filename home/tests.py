from django.test import TestCase


class HomeLinksTests(TestCase):
    def test_home_renders_links_from_context(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="https://portal.muralhapaulista.sp.gov.br/"')
        self.assertContains(response, 'src="https://portal.muralhapaulista.sp.gov.br/assets/icon/favicon-sp.png"')
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, 'rel="noopener noreferrer"')
        self.assertContains(response, "Portal Muralha Paulista")
