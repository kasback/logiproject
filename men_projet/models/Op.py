from odoo import fields, models, api


class Op(models.Model):
    _name = "men_projet.op"
    _rec_name = 'nom'

    sequence = fields.Char('Sequence', readonly=True)
    nom = fields.Char('Nom')
    responsable = fields.Many2one('res.partner')
    programme_id = fields.Many2one('men_projet.programme')
    os_id = fields.Many2one('men_projet.os')
    programme_id_value = fields.Integer(compute="_get_programme_id")
    risques = fields.One2many('men_projet.risque', 'op_id')
    indicateurs = fields.One2many('men_projet.indicateur', 'op_id')
    indicateur_efficacite = fields.Float('Indicateur d\'éfficacité')
    description = fields.Text()

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

    @api.onchange('os_id')
    def _get_programme_id(self):
        for op in self:
            context = self._context
            op.programme_id_value = context.get('programme_id')

    @api.model
    def create(self, vals):
        res = super(Op, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('men_projet.op') or '/'
        res['sequence'] = seq
        return res

    planif_status = fields.Char(compute=lambda self: self._get_planif_status())

    def _get_planif_status(self):
        self.planif_status = self._context.get('planif_status')


class Ressource(models.Model):
    _name = "men_projet.ressource"
    _rec_name = 'nom'

    nom = fields.Char('Nom')
    tel = fields.Char('Téléphone')
    email = fields.Char('Email')
    profession = fields.Char('Profession')
    profil = fields.Char('Profil')
    diplome = fields.Char('Dîplome')
    p_o = fields.Char('Poste Occupé')
    nbr_exp = fields.Integer('Nombre d\'années d\'éxpérience')
    comp_cle = fields.Char('Compétences Clefs')


class PartiePrenante(models.Model):
    _name = "men_projet.pp"
    _rec_name = 'nom'

    nom = fields.Char('Nom')
    op_id = fields.Many2many('men_projet.op')


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



