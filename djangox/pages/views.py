from django.views.generic import TemplateView
from accounts.models import StellarAccount
from accounts.utils import getAssets, getClaimableBalances, getOperations
import dateutil.parser

class HomePageView(TemplateView):

    def get_template_names(self):
        if not self.request.user.is_anonymous:
            template_name = 'pages/home.html'
        else:
            print('exec')
            template_name = 'pages/launchaco.html'
        return template_name

    def get_context_data(self, *args, **kwargs):
        """
        Render Balances and Claimable balances :D
        """
        # Create Context
        context = super(HomePageView, self).get_context_data(*args, **kwargs)
        user = self.request.user
        if not user.is_anonymous:
            try:
                public_key = StellarAccount.objects.filter(accountId=user)[0].public_key
            
                # Get Assets
                assets = getAssets(public_key)
                context["balances"] = assets
                
                # Get claimable balances
                balances = getClaimableBalances(public_key)
                context["claimable_balances"] = balances

                operations = getOperations(public_key)
                context["operations"] = operations

                counts = {}
                for operation in operations:
                    date = dateutil.parser.isoparse(operation["created_at"])
                    date = f"{date.year}-{date.month}-{date.day}"
                    if counts.get(date) is not None: 
                        counts[date] += 1 
                    else:
                        counts[date] = 1
                
                context["bar_chart_labels"] = list(counts.keys())
                context["bar_chart_values"] = list(counts.values())

                
            except:
                pass
            return context



class AboutPageView(TemplateView):
    template_name = 'pages/about.html'