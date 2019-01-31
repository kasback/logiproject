from odoo import models, fields, api


class Programme(models.Model):
    _name = 'men_projet.programme'
    _rec_name = 'nom'
    _defaluts = {
        'objectif_type': 'all',
    }

    sequence = fields.Char('Sequence', readonly=True)
    nom = fields.Char('Intitulé', required="True")
    responsable = fields.Many2one('res.partner')
    os = fields.One2many('men_projet.os', 'programme_id', string="Objectifs Stratégiques")
    os_none_edit = fields.One2many('men_projet.os', 'programme_id', string="Objectifs Stratégiques")
    os_suivi = fields.One2many('men_projet.os', 'programme_id', string="Objectifs Stratégiques")
    op = fields.One2many('men_projet.op', 'programme_id', string="Objectifs Projets")
    op_none_edit = fields.One2many('men_projet.op', 'programme_id', string="Objectifs Projets")
    op_suivi = fields.One2many('men_projet.op', 'programme_id', string="Objectifs Projets")
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
        ('all', 'Voir tout'),
        ('osg', 'Objectif global'),
        ('os', 'Objectifs stratégiques'),
        ('op', 'Objectifs projets')
    ], default='all', string="Filtrer par objectif")

    res = [
        ('osg', 'Objectif global'),
        ('os', 'Objectifs stratégiques'),
        ('op', 'Objectifs projets')
    ]

    @api.multi
    def _set_risques_domain(self):
        res = {}
        for programme in self:
            if programme.status == 'planification':
                res['domain'] = {'risques': [('risque_type', '=', programme.planif_status)]}
            elif programme.status == 'suivi':
                res['domain'] = {'risques': [('programme_id', '=', programme.id)]}
                self.risques_suivi = self.env['men_projet.risque'].search([('programme_id', '=', programme.id)])
                self.indicateurs_suivi = self.env['men_projet.indicateur'].search([('programme_id', '=', programme.id)])
            domain = res.get('domain')

            if domain is not None:
                return domain.get('risques')

    @api.onchange('objectif_type')
    def _filter_indicateur(self):
        print('inside onchange')
        programme_id = self._origin.id
        if programme_id:
            if self.objectif_type is not False:
                if self.objectif_type != 'all':
                    indicateurs = self.env['men_projet.indicateur'].search(['&', ('o_type', '=', self.objectif_type),
                                                                            ('programme_id', '=', programme_id)])
                else:
                    indicateurs = self.env['men_projet.indicateur'].search([('programme_id', '=', programme_id)])
            self.indicateurs_suivi = indicateurs

    @api.onchange('objectif_type')
    def _filter_risques(self):
        programme_id = self._origin.id
        if self.objectif_type is not False:
            if self.objectif_type == 'osg':
                risques = self.env['men_projet.risque'].search(['&', ('risque_type', '=', 'risques_globaux'),
                                                                ('programme_id', '=', programme_id)])
            elif self.objectif_type == 'os':
                risques = self.env['men_projet.risque'].search(['&', ('risque_type', '=', 'risques_strategiques')
                                                                   , ('programme_id', '=', programme_id)])
            elif self.objectif_type == 'op':
                risques = self.env['men_projet.risque'].search(['&', ('risque_type', '=', 'risques_projets')
                                                                   , ('programme_id', '=', programme_id)])
            elif self.objectif_type == 'all':
                risques = self.env['men_projet.risque'].search([('programme_id', '=', programme_id)])
        self.risques_suivi = risques

    risques = fields.One2many('men_projet.risque', 'programme_id', domain=lambda self: self._set_risques_domain())
    risques_suivi = fields.One2many('men_projet.risque', 'programme_id', store=True)
    risques_osg = fields.One2many('men_projet.risque', 'programme_id', domain=[('risque_type', '=', 'risques_globaux')])
    risques_os = fields.One2many('men_projet.risque', 'programme_id',
                                 domain=[('risque_type', '=', 'risques_strategiques')])
    risques_op = fields.One2many('men_projet.risque', 'programme_id', domain=[('risque_type', '=', 'risques_projets')])
    risques_non_planif = fields.One2many('men_projet.risque_non_planif', 'programme_id', string='Risques non planifiés')
    indicateurs_suivi = fields.One2many('men_projet.indicateur', 'programme_id', store=True)
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
        res['os_global_suivi'] = res['os_global']
        return res

    @api.multi
    def write(self, vals):
        print(self._context)
        vals['objectif_type'] = 'all'
        if 'indicateurs_suivi' in vals:
            indicateurs = vals['indicateurs_suivi']
            for indicateur in indicateurs:
                if indicateur[2] and indicateur[2] is not False and type(indicateur[2]) == dict:
                    val_cible = indicateur[2]['valeurs_cibles']
                    for vc in val_cible:
                        if vc[2] is not False:
                            self.env['men_projet.vc'].search([('id', '=', vc[1])]).write(vc[2])

        if 'risques_suivi' in vals:
            risques = vals['risques_suivi']
            for risque in risques:
                if risque[2] and risque[2] is not False and type(risque[2]) == dict:
                    survenues = risque[2]['survenues']
                    for survenu in survenues:
                        if survenu[2] is not False:
                            # print('survenu[2] : ' + str(survenu[2]))
                            # print('risque id : ' + str(risque[1]) + ' ses survenues : ' + str(survenu[2]))
                            self.env['men_projet.survenue'].search([('id', '=', risque[1])]).write(survenu[2])

        vals['indicateurs_suivi'] = self.env['men_projet.indicateur'].search([('programme_id', '=', self.id)])
        vals['risques_suivi'] = self.env['men_projet.risque'].search([('programme_id', '=', self.id)])

        return super(Programme, self).write(vals)


class OsGlobal(models.Model):
    _name = "men_projet.os_global"
    _rec_name = 'nom'

    sequence = fields.Char('Sequence', readonly=True)
    nom = fields.Char('Intitulé')
    responsable = fields.Many2one('res.partner')
    os = fields.One2many('men_projet.os', 'osg_id')
    risques = fields.One2many('men_projet.risque', 'osg_id')
    indicateurs = fields.One2many('men_projet.indicateur', 'osg_id')
    indicateur_efficacite = fields.Float('Taux d\'éfficacité')
    description = fields.Text('Description')

    @api.model
    def create(self, vals):
        record = super(OsGlobal, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('men_projet.osg') or '/'
        record['sequence'] = seq
        return record
