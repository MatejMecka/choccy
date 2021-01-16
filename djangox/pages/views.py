from django.views.generic import TemplateView
from accounts.models import StellarAccount
from accounts.utils import getAssets, getClaimableBalances

class HomePageView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, *args, **kwargs):
        """
        Render Balances and Claimable balances :D
        """
        # Create Context
        context = super(HomePageView, self).get_context_data(*args, **kwargs)
        user = self.request.user
        if not user.is_anonymous:
            public_key = StellarAccount.objects.filter(accountId=user)[0].public_key
            # Get Assets
            assets = getAssets(public_key)
            context["balances"] = assets
            
            # Get claimable balances
            balances = getClaimableBalances(public_key)
            context["claimable_balances"] = balances
            
            return context



class AboutPageView(TemplateView):
    template_name = 'pages/about.html'