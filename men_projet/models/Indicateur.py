from odoo import models, fields, api


class Indicateur(models.Model):
    _name = 'men_projet.indicateur'
    _rec_name = 'intitule'

    sequence = fields.Char('Sequence', readonly=True)
    intitule = fields.Char()
    type = fields.Selection([('quantitatif', 'Quantitatif'),
                             ('qualitatif', 'Qualitatif'),
                             ('qualitatif_quantifiable', 'Qualitatif quantifiable'),
                             ('delai', 'Délai'),
                             ('cout', 'Coût'),
                             ('lieu', 'Lieu')])
    responsable = fields.Many2one('res.partner')
    sprint = fields.Selection([('journalier', 'Journalier'),
                               ('hebdomadaire', 'Hebdomadaire'),
                               ('quinzaine', 'Quinzaine'),
                               ('mensuel', 'Mensuel'),
                               ('trimestriel', 'Trimestriel'),
                               ('semestriel', 'Semestriel'),
                               ('annuel', 'Annuel'),
                               ])
    date_debut = fields.Date()
    date_fin = fields.Date()
    delai = fields.Integer()
    seuil1 = fields.Float('Seuil 1')
    seuil2 = fields.Float('Seuil 2')
    coef_eff = fields.Integer('Coefficient d\'efficacité')
    coef_pond = fields.Integer('Coefficient de pondération')
    val_min = fields.Float('Valeur min')
    val_max = fields.Float('Valeur max')
    val_init = fields.Float('Valeur initiale')
    val_finale = fields.Float('Valeur finale')
    unite_mesure = fields.Many2one('uom.uom', 'Unité de mesure')
    os_id = fields.Many2one('men_projet.os', domain=lambda self: self._set_objectifs_domain())
    osg_id = fields.Many2one('men_projet.os_global')
    op_id = fields.Many2one('men_projet.op', domain=lambda self: self._set_objectifs_domain())
    o_type = fields.Char()
    indicateur_parent = fields.Many2one('men_projet.indicateur', domain=lambda self: self._set_indicateur_parent_domain())
    indicateurs_lies = fields.One2many('men_projet.indicateur', 'indicateur_parent')
    si = fields.One2many('men_projet.si', 'indicateur_id')
    norme = fields.Char()
    valeurs_cibles = fields.One2many('men_projet.vc', 'indicateur_id')
    programme_id = fields.Many2one('men_projet.programme')
    reference = fields.Many2one('men_projet.in_ref')
    echelle = fields.Selection([(1, 1), (2, 2), (3, 3), (4, 4), (5, 5),
                                (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], string="Echelle")
    description = fields.Text('Description')

    @api.model
    def create(self, vals):
        record = super(Indicateur, self).create(vals)
        programme_id = 0
        if record.osg_id:
            programme_id = self._context.get('programme_id')
            record['o_type'] = 'osg'
        if record.os_id:
            programme_id = self.env['men_projet.os'].search([('id', '=', record.os_id.id)]).programme_id
            record['o_type'] = 'os'
        if record.op_id:
            programme_id = self.env['men_projet.op'].search([('id', '=', record.op_id.id)]).programme_id
            record['o_type'] = 'op'
        record['programme_id'] = programme_id
        seq = self.env['ir.sequence'].next_by_code('men_projet.indicateur') or '/'
        record['sequence'] = seq
        return record

    def _set_indicateur_parent_domain(self):
        programme_id = self._context.get('programme_id')
        o_type = self._context.get('o_type')
        res = {}
        if o_type == 'os':
            res['domain'] = {'indicateur_parent': ['&', ('programme_id', '=', programme_id), ('o_type', '=', 'osg')]}
        elif o_type == 'op':
            res['domain'] = {'indicateur_parent': ['&', ('programme_id', '=', programme_id), ('o_type', '=', 'os')]}
        if res.get('domain'):
            return res.get('domain').get('indicateur_parent')

    @api.onchange('os_id')
    def _set_objectifs_domain(self):
        programme_id = self._context.get('programme_id')
        o_type = self._context.get('o_type')
        res = {}
        if o_type == 'os':
            res['domain'] = {'os_id': [('programme_id', '=', programme_id)]}
        elif o_type == 'op':
            res['domain'] = {'op_id': [('programme_id', '=', programme_id)]}
        return res


class SourceInformation(models.Model):
    _name = "men_projet.si"
    _rec_name = "intitule"

    intitule = fields.Char('Intitulé')
    responsable = fields.Many2one('res.partner')
    indicateur_id = fields.Many2one('men_projet.indicateur')


class ValeursCible(models.Model):
    _name = "men_projet.vc"

    indicateur_id = fields.Many2one('men_projet.indicateur')
    vc = fields.Float('Valeur cible')
    vr = fields.Float('Valeur réelle')
    ecart = fields.Char('Écart', compute="_calc_ecart")
    t_r = fields.Char('Taux de réalisation', compute="_calc_taux_realisation")
    date_cible = fields.Date('Date cible')
    date_saisie = fields.Date('Date réelle')
    analyse = fields.Text()
    ajustement = fields.Text()

    @api.depends('vr')
    def _calc_ecart(self):
        for record in self:
            if record.vr:
                record.ecart = float(record.vc) - float(record.vr)

    @api.depends('ecart')
    def _calc_taux_realisation(self):
        for record in self:
            if record.ecart:
                record.t_r = str(round((100 - ((float(record.ecart) / float(record.vc)) * 100)), 2)) + '%'


class InRef(models.Model):
    _name = "men_projet.in_ref"
    _rec_name = 'intitule'

    intitule = fields.Char(string="intitulé")
