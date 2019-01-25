from odoo import fields, models, api


class Risque(models.Model):
    _name = "men_projet.risque"
    _rec_name = 'intitule'

    sequence = fields.Char('Sequence', readonly=True)
    intitule = fields.Char('Intitulé')
    description = fields.Text('Description')
    source = fields.Many2one('men_projet.sources_risque')
    echelle = fields.Selection([(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], string="Echelle Probabilité en %")
    valeur = fields.Float('Valeur')
    impacte = fields.Text('Description d\'impacte')
    gravite = fields.Integer('Echelle gravité')
    criticite = fields.Integer(compute="_calc_criticite", string='Criticité')
    mesuresPre = fields.Many2one('men_projet.mesure', domain="[('type', '=', 'prev')]", string='Mesures Préventives')
    mesuresUrg = fields.Many2one('men_projet.mesure', domain="[('type', '=', 'urg')]", string='Mesures Urgentes')
    mesuresCorr = fields.Many2one('men_projet.mesure', domain="[('type', '=', 'corr')]", string='Mesures Corréctives')
    programme_id = fields.Many2one('men_projet.programme')
    os_id = fields.Many2one('men_projet.os', 'Objectif stratégique')
    osg_id = fields.Many2one('men_projet.os_global', 'Objectif global')
    op_id = fields.Many2one('men_projet.op', 'Objectif projet')
    o_type = fields.Char(compute="_get_type_o")
    risque_type = fields.Char()
    survenues = fields.One2many('men_projet.survenue', 'risque_id')
    with_survenu = fields.Boolean(compute="_check_if_survenu")

    @api.onchange('echelle', 'gravite')
    def _calc_criticite(self):
        for risque in self:
            risque.criticite = risque.gravite * risque.echelle

    @api.onchange('with_survenu')
    def _check_if_survenu(self):
        context = self._context
        for risque in self:
            status = context.get('status')
            if status == 'planification':
                risque.with_survenu = False
            else:
                risque.with_survenu = True

    @api.onchange('description')
    def _get_type_o(self):
        context = self._context
        res = {}
        programme = context.get('programme')
        objectif = context.get('objectif')
        for risque in self:
            if objectif == 'risques_globaux':
                risque.o_type = 'risques_globaux'
                risque.risque_type = risque.o_type
                res['domain'] = {'os_global': [('programme_id', '=', programme)]}
            elif objectif == 'risques_strategiques':
                risque.o_type = 'risques_strategiques'
                res['domain'] = {'os_id': [('programme_id', '=', programme)]}
                risque.risque_type = risque.o_type
            elif objectif == 'risques_projets':
                risque.o_type = 'risques_projets'
                res['domain'] = {'op_id': [('programme_id', '=', programme)]}
                risque.risque_type = risque.o_type
            return res

    @api.model
    def create(self, vals):
        res = super(Risque, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('men_projet.risque') or '/'
        res['sequence'] = seq
        return res


class Mesure(models.Model):
    _name = "men_projet.mesure"
    _rec_name = 'intitule'

    intitule = fields.Char('Intitulé')
    type = fields.Selection([
        ('prev', 'Mesures Préventives'),
        ('urg', 'Mesures Urgentes'),
        ('corr', 'Mesures Corréctives'),
    ])


class Survenue(models.Model):
    _name = "men_projet.survenue"

    survenu = fields.Boolean(default=False)
    date_survenu = fields.Date()
    risque_id = fields.Many2one('men_projet.risque')
    impacte_reel = fields.Char()


class SourcesRisque(models.Model):
    _name = "men_projet.sources_risque"
    _rec_name = "intitule"

    intitule = fields.Char()

