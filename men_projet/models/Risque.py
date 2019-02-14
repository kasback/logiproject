from odoo import fields, models, api


class Risque(models.Model):
    _name = "men_projet.risque"
    _rec_name = 'intitule'

    sequence = fields.Char('Sequence', readonly=True)
    code = fields.Char('Code')
    intitule = fields.Char('Intitulé')
    description = fields.Text('Description')
    source = fields.Many2one('men_projet.sources_risque')
    echelle = fields.Selection([(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], string="Echelle Probabilité en %")
    valeur = fields.Float('Valeur')
    impacte = fields.Text('Description d\'impact')
    gravite = fields.Integer('Echelle gravité')
    criticite = fields.Integer(compute="_calc_criticite", string='Criticité')
    mesuresPre = fields.One2many('men_projet.mesure', 'risque_id', string='Mesures Préventives',
                                 domain=[('m_type', '=', 'mesure_preventive')])
    mesuresUrg = fields.One2many('men_projet.mesure', 'risque_id',  string='Mesures Urgentes',
                                 domain=[('m_type', '=', 'mesure_urgente')])
    mesuresCorr = fields.One2many('men_projet.mesure', 'risque_id', string='Mesures Corréctives',
                                  domain=[('m_type', '=', 'mesure_corrective')])
    programme_id = fields.Many2one('men_projet.programme')
    os_id = fields.Many2one('men_projet.os', 'Objectif stratégique', default=lambda self: self.env['men_projet.os'].search([('id', '=', self._context.get('os_filter'))]))
    osg_id = fields.Many2one('men_projet.os_global', 'Objectif global')
    op_id = fields.Many2one('men_projet.op', 'Objectif projet', default=lambda self: self.env['men_projet.op'].search([('id', '=', self._context.get('op_filter'))]))
    oi_id = fields.Many2one('men_projet.oi', 'Livrables')
    oo_id = fields.Many2one('men_projet.oo', 'Activités')
    soo_id = fields.Many2one('men_projet.soo', 'Tâche')
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
                risque.risque_type = risque.o_type
            elif objectif == 'risques_projets':
                risque.o_type = 'risques_projets'
                risque.risque_type = risque.o_type
            elif objectif == 'risques_oin':
                risque.o_type = 'risques_oin'
                risque.risque_type = risque.o_type
            elif objectif == 'risques_oo':
                risque.o_type = 'risques_oo'
                risque.risque_type = risque.o_type
            elif objectif == 'risques_soo':
                risque.o_type = 'risques_soo'
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
    description = fields.Text('Description')
    type = fields.Many2one('men_projet.mesure_type')
    risque_id = fields.Many2one('men_projet.risque')
    risque_nonplanif_id = fields.Many2one('men_projet.risque_non_planifie')
    m_type = fields.Char(default=lambda self: self._context.get('m_type'))

    @api.model
    def create(self,vals):
        res = super(Mesure, self).create(vals)
        return res


class MesureType(models.Model):
    _name = "men_projet.mesure_type"
    _rec_name = 'intitule'

    intitule = fields.Char('Intitulé')
    description = fields.Text('Description')


class Survenue(models.Model):
    _name = "men_projet.survenue"

    survenu = fields.Boolean(default=False, string="Occurence")
    date_survenu = fields.Date('Date d\'occurrence')
    risque_id = fields.Many2one('men_projet.risque')
    impacte_reel = fields.Text('Impact réél')


class SourcesRisque(models.Model):
    _name = "men_projet.sources_risque"
    _rec_name = "intitule"

    intitule = fields.Char('Intitulé')
    description = fields.Text('Description')


class RisqueNonPlanifie(models.Model):
    _name = "men_projet.risque_non_planif"
    _rec_name = 'intitule'

    intitule = fields.Char('Intitulé')
    description = fields.Text('Description')
    source = fields.Many2one('men_projet.sources_risque')
    mesuresUrg = fields.One2many('men_projet.mesure', 'risque_nonplanif_id', string='Mesures Urgentes',
                                 domain=[('m_type', '=', 'mesure_urgente')])
    mesuresCorr = fields.One2many('men_projet.mesure', 'risque_nonplanif_id', string='Mesures Corréctives',
                                  domain=[('m_type', '=', 'mesure_corrective')])
    programme_id = fields.Many2one('men_projet.programme')
    op_id = fields.Many2one('men_projet.op')
    date_survenu = fields.Date('Date d\'occurrence')



