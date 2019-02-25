from odoo import fields, models, api


class Op(models.Model):
    _name = "men_projet.op"
    _rec_name = 'nom'

    sequence = fields.Char('Sequence', readonly=True)
    code = fields.Char('Code')
    nom = fields.Char('Intitulé')
    responsable = fields.Many2one('res.partner')
    programme_id = fields.Many2one('men_projet.programme', string="Intitulé du programme")

    @api.multi
    def _set_risques_domain(self):
        res = {}
        for op in self:
            if op.status == 'planification':
                res['domain'] = {'risques': [('risque_type', '=', op.planif_status_wf)]}
            elif op.status == 'suivi':
                res['domain'] = {'risques': [('op_id', '=', op.id)]}
                self.risques_suivi = self.env['men_projet.risque'].search([('op_id', '=', op.id)])
                self.indicateurs_suivi = self.env['men_projet.indicateur'].search([('op_id', '=', op.id)])
            domain = res.get('domain')

            if domain is not None:
                return domain.get('risques')

    risques = fields.One2many('men_projet.risque', 'op_id', domain=lambda self: self._set_risques_domain())
    indicateurs = fields.One2many('men_projet.indicateur', 'op_id', domain=[('o_type', '=', 'op')])
    indicateur_efficacite = fields.Float('Taux d\'éfficacité')
    description = fields.Text()
    indicateurs_suivi = fields.One2many('men_projet.indicateur', 'op_id', store=True)
    risques_suivi = fields.One2many('men_projet.risque', 'op_id', store=True)
    risques_non_planif = fields.One2many('men_projet.risque_non_planif', 'op_id', string='Risques non planifiés')

    # fiche projet

    maitre_ouvrage = fields.Many2one('men_projet.pp', string='Maître d\'ouvrage')
    maitre_oeuvre = fields.Many2one('men_projet.pp', string='Maître d\'oeuvre')
    type = fields.Many2one('men_projet.projet_type', string='Type')
    livrable = fields.Char('Livrable')
    date_debut = fields.Date('Date début')
    date_fin = fields.Date('Date fin')
    budget = fields.Float('Budget')
    cout_reel = fields.Float('Coût Réel')
    chef_projet = fields.Many2one('men_projet.ressource')
    directeur_projet = fields.Many2one('men_projet.ressource')
    comites = fields.Many2many('men_projet.staff')
    equipe_operation = fields.Many2many('men_projet.ressource', string="Equipe opérationnelle")
    autres_participants = fields.Many2many('men_projet.autre_ressource', string="Autres Participants")
    os_id = fields.Many2one('men_projet.os', 'Objectif stratégique',
                            default=lambda self: self.env['men_projet.os'].search([('id', '=', self._context.get('os_filter'))]))

    status = fields.Selection([
        ('planification', 'Planification'),
        ('suivi', 'Suivi et evaluation'),
    ], default='planification')

    planif_status_wf = fields.Selection([
        ('objectifs_projets', 'Objectif projet'),
        ('objectifs_intermediaires', 'Livrables'),
        ('objectifs_operationnels', 'Activités'),
        ('s_objectifs_operationnels', 'Tâches'),
        ('risques_soo', 'Risques de Tâches'),
        ('risques_oo', 'Risques d\'activités'),
        ('risques_oin', 'Risque Livrables'),
    ], default='objectifs_projets')

    suivi_status = fields.Selection([
        ('suivi_indicateur', 'Suivi des indicateurs'),
        ('suivi_risques', 'Suivi des risques'),
        ('suivi_objectifs', 'Suivi des objectifs')
    ])

    @api.one
    def livrables_btn(self):
        self.write({
            'planif_status_wf': 'objectifs_intermediaires',
        })

    @api.one
    def activites_btn(self):
        self.write({
            'planif_status_wf': 'objectifs_operationnels',
        })

        # os = self.env['men_projet.os'].search([('programme_id', '=', self.id)])
        # for os_item in os:
        #     os_item.write({
        #         'osg_id': self.os_global.id
        #     })

    @api.one
    def taches_btn(self):
        self.write({
            'planif_status_wf': 's_objectifs_operationnels',
        })

    @api.one
    def risques_livrables_btn(self):
        self.write({
            'planif_status_wf': 'risques_oin',
        })

    @api.one
    def risques_activites_btn(self):
        self.write({
            'planif_status_wf': 'risques_oo',
        })\


    @api.one
    def risques_taches_btn(self):
        self.write({
            'planif_status_wf': 'risques_soo',
        })

    @api.model
    def create(self, vals):
        res = super(Op, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('men_projet.op') or '/'
        res['sequence'] = seq
        return res

    planif_status = fields.Char(compute=lambda self: self._get_planif_status())

    def _get_planif_status(self):
        self.planif_status = self._context.get('planif_status')

    pps = fields.One2many('men_projet.pp', 'op_id', string="Parties Prenantes")
    ois = fields.One2many('men_projet.oi', 'op_id', string='Livrables')
    oos = fields.One2many('men_projet.oo', 'op_id', string='Activités')
    soos = fields.One2many('men_projet.soo', 'op_id', string='Tâches')
    suivi_ois = fields.One2many('men_projet.oi', 'op_id', string='Livrables')
    suivi_oos = fields.One2many('men_projet.oo', 'op_id', string='Activités')
    suivi_soos = fields.One2many('men_projet.soo', 'op_id', string='Tâches')


class Ressource(models.Model):
    _name = "men_projet.ressource"
    _rec_name = 'nom'

    nom = fields.Char('Nom')
    description = fields.Text('Description')
    tel = fields.Char('Téléphone')
    email = fields.Char('Email')
    profession = fields.Char('Profession')
    profil = fields.Char('Profil')
    diplome = fields.Char('Dîplome')
    p_o = fields.Char('Poste Occupé')
    nbr_exp = fields.Integer('Nombre d\'années d\'éxpérience')
    comp_cle = fields.Char('Compétences Clefs')
    op_id = fields.Many2many('men_projet.op')


class AutreRessource(models.Model):
    _name = "men_projet.autre_ressource"
    _rec_name = 'nom'

    nom = fields.Char('Nom')
    description = fields.Text('Description')
    tel = fields.Char('Téléphone')
    email = fields.Char('Email')
    profession = fields.Char('Profession')
    profil = fields.Char('Profil')
    diplome = fields.Char('Dîplome')
    p_o = fields.Char('Poste Occupé')
    nbr_exp = fields.Integer('Nombre d\'années d\'éxpérience')
    comp_cle = fields.Char('Compétences Clefs')
    op_id = fields.Many2many('men_projet.op', string="Objectif Projet")


class PartiePrenante(models.Model):
    _name = "men_projet.pp"
    _rec_name = 'nom'

    sequence = fields.Char('Sequence', readonly=True)
    nom = fields.Char('Nom')
    description = fields.Text('Description')
    interet = fields.Char('intérêt')
    besoins = fields.One2many('men_projet.besoins_pp', 'pp_id', string='Besoin')
    impact = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10')
    ], string="Impact")
    influence = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10')
    ], string="Influence")
    role = fields.Char('Rôle')
    risques = fields.One2many('men_projet.risques_pp', 'pp_id', string="Risques")
    engagements = fields.One2many('men_projet.engagements_pp', 'pp_id', string="Engagements")
    relations = fields.One2many('men_projet.relations_pp', 'pp_id', string="Relations")
    op_id = fields.Many2one('men_projet.op')


class RisquePp(models.Model):
    _name = "men_projet.risques_pp"
    _rec_name = 'nom'

    nom = fields.Char('Nom')
    pp_id = fields.Many2one('men_projet.pp')


class EngagementsPp(models.Model):
    _name = "men_projet.engagements_pp"
    _rec_name = 'nom'

    nom = fields.Char('Nom')
    pp_id = fields.Many2one('men_projet.pp')


class RelationsPp(models.Model):
    _name = "men_projet.relations_pp"
    _rec_name = 'nom'

    nom = fields.Char('Nom')
    pp_id = fields.Many2one('men_projet.pp')


class BesoinsPp(models.Model):
    _name = "men_projet.besoins_pp"
    _rec_name = 'nom'

    nom = fields.Char('Nom')
    pp_id = fields.Many2one('men_projet.pp')


class ProjetType(models.Model):
    _name = "men_projet.projet_type"
    _rec_name = 'nom'

    nom = fields.Char('Nom')


class Staff(models.Model):
    _name = "men_projet.staff"
    _rec_name = 'nom'

    nom = fields.Char('Nom')
    mission = fields.Char('Mission')
    description = fields.Char('Description')
    ressource_id = fields.Many2one('men_projet.ressource')
    projets = fields.Many2many('men_projet.op')



