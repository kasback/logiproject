from odoo import models, fields, api


class Programme(models.Model):
    _name = 'men_projet.programme'
    _rec_name = 'nom'

    sequence = fields.Char('Sequence', readonly=True)
    nom = fields.Char('Intitulé', required="True")
    responsable = fields.Many2one('res.partner')
    os = fields.One2many('men_projet.os', 'programme_id')
    os_none_edit = fields.One2many('men_projet.os', 'programme_id')
    os_suivi = fields.One2many('men_projet.os', 'programme_id')
    op = fields.One2many('men_projet.op', 'programme_id')
    op_none_edit = fields.One2many('men_projet.op', 'programme_id')
    op_suivi = fields.One2many('men_projet.op', 'programme_id')
    description = fields.Text('Description')
    status = fields.Selection([
        ('planification', 'Planification'),
        ('suivi', 'Suivi et evaluation'),
    ], default='planification')

    planif_status = fields.Selection([
        ('objectifs_globaux', 'Objectifs global'),
        ('objectifs_strategiques', 'Objectifs stratégiques'),
        ('objectifs_projets', 'Objectifs Projets'),
        ('risques_projets', 'Risques Projets'),
        ('risques_strategiques', 'Risques stratégiques'),
        ('risques_globaux', 'Risques globaux')
    ], default='objectifs_globaux')

    suivi_status = fields.Selection([
        ('suivi_indicateur', 'Suivi des indicateurs'),
        ('suivi_risques', 'Suivi des risques'),
        ('suivi_objectifs', 'Suivi des objectifs')
    ])

    objectif_type = fields.Selection(selection=[
        ('osg', 'Objectif global'),
        ('os', 'Objectifs stratégiques'),
        ('op', 'Objectifs projets')
    ], default='osg', string="Filtrer par objectif")

    @api.multi
    def _set_risques_domain(self):
        res = {}
        for programme in self:
            if programme.status == 'planification':
                res['domain'] = {'risques': [('risque_type', '=', programme.planif_status)]}
            elif programme.status == 'suivi':
                res['domain'] = {'risques': [('programme_id', '=', programme.id)]}
            domain = res.get('domain')

            if domain is not None:
                return domain.get('risques')

    @api.onchange('objectif_type')
    def _filter_indicateur(self):
        if self.objectif_type is not False:
            indicateurs = self.env['men_projet.indicateur'].search([('o_type', '=', self.objectif_type)])
        else:
            indicateurs = self.env['men_projet.indicateur'].search([('o_type', 'in', ['osg', 'os', 'op'])])
        self.indicateurs = indicateurs

    @api.onchange('objectif_type')
    def _filter_risques(self):
        if self.objectif_type is not False:
            if self.objectif_type == 'osg':
                risques = self.env['men_projet.risque'].search([('risque_type', '=', 'risques_globaux')])
            elif self.objectif_type == 'os':
                risques = self.env['men_projet.risque'].search([('risque_type', '=', 'risques_strategiques')])
            elif self.objectif_type == 'op':
                risques = self.env['men_projet.risque'].search([('risque_type', '=', 'risques_projets')])
        else:
            risques = self.env['men_projet.risque']\
                .search([('risque_type', 'in', ['risques_globaux', 'risques_strategiques', 'risques_projets'])])
        self.risques_suivi = risques

    risques = fields.One2many('men_projet.risque', 'programme_id', domain=lambda self: self._set_risques_domain())
    risques_suivi = fields.One2many('men_projet.risque', 'programme_id', compute=lambda self: self._filter_risques())
    risques_osg = fields.One2many('men_projet.risque', 'programme_id', domain=[('risque_type', '=', 'risques_globaux')])
    risques_os = fields.One2many('men_projet.risque', 'programme_id', domain=[('risque_type', '=', 'risques_strategiques')])
    risques_op = fields.One2many('men_projet.risque', 'programme_id', domain=[('risque_type', '=', 'risques_projets')])
    indicateurs = fields.One2many('men_projet.indicateur', 'programme_id',
                                  compute=lambda self: self._filter_indicateur())
    os_global = fields.Many2one('men_projet.os_global')
    os_global_suivi = fields.Many2one('men_projet.os_global')

    @api.one
    def objectifs_strategiques_btn(self):
        self.write({
            'planif_status': 'objectifs_strategiques',
        })

    @api.one
    def objectifs_projets_btn(self):
        self.write({
            'planif_status': 'objectifs_projets',
        })

        os = self.env['men_projet.os'].search([('programme_id', '=', self.id)])
        for os_item in os:
            os_item.write({
                'osg_id': self.os_global.id
            })

    @api.one
    def risques_projets_btn(self):
        self.write({
            'planif_status': 'risques_projets',
        })


    @api.one
    def risques_strategiques_btn(self):
        self.write({
            'planif_status': 'risques_strategiques',
        })

    @api.one
    def risques_globaux_btn(self):
        self.write({
            'planif_status': 'risques_globaux',
        })

    @api.model
    def create(self, vals):
        res = super(Programme, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('men_projet.programme') or '/'
        res['sequence'] = seq
        return res


class OsGlobal(models.Model):
    _name = "men_projet.os_global"
    _rec_name = 'nom'

    sequence = fields.Char('Sequence', readonly=True)
    nom = fields.Char('Intitulé')
    responsable = fields.Many2one('res.partner')
    os = fields.One2many('men_projet.os', 'osg_id')
    risques = fields.One2many('men_projet.risque', 'osg_id')
    indicateurs = fields.One2many('men_projet.indicateur', 'osg_id')
    indicateur_efficacite = fields.Float('Indicateur d\'éfficacité')
    description = fields.Char()

    @api.model
    def create(self, vals):
        record = super(OsGlobal, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('men_projet.osg') or '/'
        record['sequence'] = seq
        return record



