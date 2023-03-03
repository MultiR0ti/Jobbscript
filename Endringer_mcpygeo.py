

#soil.py
'''
DTYPE = {
    'z_min': 'float',
    'z_max': 'float',
    'soil_type': str,
    'gamma_eff': 'float',
    'phi': 'float',
    'side_quake': 'float',
    'toe_quake': 'float',
    'side_damping': 'float',
    'toe_damping': 'float',
    'f_st': 'float',
    'qt': 'float',
    'fs': 'float',
    'qp': 'float',
    'br': 'float',
    'qc': 'float', # Ukorrigert spissmotstand
    'su_uu': 'float' # Udrenert skjærstyrke i leire
}

'''

#

#pile_capacity
'''

SOIL_COEFF_NGI99 = {
    'c': {
        'friction': {
            'ac': 80,
            'bc': 0,
            'cc': -0.25,
        },
        'toe': {
            'ktc': 0.4,
        },
    },
    's': {
        'friction': {
            'ass': 44,
            'bs': 0.3,
            'cs': -0.4,
        },
        'toe': {
            'kts': 0.15,
        },
    },
}

def ngi99(
geom_data: t.Dict,
soil_data: t.Dict,
depth: float,
closed_pile: bool = False,
depth_incr: float = 1.0,
dsf_o: float = 1.0,
compression: bool = True,
refpressure: int = 100, #JDR
**kwargs,
):
    # JDR: Finn ut hvordan material skal implementeres:
    material = kwargs['Material']
    #mat1 = ['s', 'steel', 'stål', 'timber', 'tre', 't', 'wood', 'w']
    mat2 = ['concrete', 'c', 'b', 'betong']
    F_mat = 1.3 if mat2.__contains__(material.lower()) else 1
    # JDR

    del kwargs
    # Initialize pile geometry
    pile = Pile(geom_data)

    # Process geometry input
    full_area_steel_tip = pile.area_toe(closed=True)

    # Initialize soil properties
    soil = Soil(soil_data)

    # Initialize result lists
    fsi = []
    qt_list = []
    plr_list = []
    resistance_best = []
    resistance_upper = []
    Q_tip = []
    Q_friction = []

    # Add new points to depths and layers to layers
    depths, layers = _generate_depths_and_layers(depth, depth_incr, soil)

    # Calculate effective stress
    eff_stress = _calculate_effective_stress(depths, layers)

    D_r = []
    plr = 0
    # Calculate capacity
    for i_depth, this_penetration in enumerate(depths):
        # Get soil type
        this_layer = layers[i_depth]
        this_soil_type = this_layer.soil_type
        su_uu = soil.layer_prop(this_penetration, 'su,uu')
        Ip = soil.layer_prop(this_penetration, 'Ip')

        # Get cpt data
        qt = 1000 * soil.cpt_prop(this_penetration, 'qt')
        qp = 1000 * soil.cpt_prop(this_penetration, 'qp')
        # JDR
        qc = 1000 * soil.cpt_prop(this_penetration, 'qc') 
        
        
        


        # Calculate friction parameters
        if this_soil_type == 's':
            a = SOIL_COEFF_NGI99[this_soil_type]['friction']['ass']
        elif this_soil_type == 'c':
            a = SOIL_COEFF_NGI99[this_soil_type]['friction']['ac']


        fsi.append(qt / a)
        qt_list.append(qt)
        

        
        # Calculate Qfriction 
        Qfr_list = []
        q_friction = []
        q_friction_equivalent = []


        # Calculate tip and friction NGI99
        #JDR
        D_r.append(0.4 * math.log(qt/(22 * math.pow(eff_stress[i_depth]*refpressure, 0.5)))) 
        F_Dr = []
        F_sig = []
        #JDR
        for i in range(i_depth + 1): #i_depth er indeksen til dybdene
            if i == 0:
                q_friction.append(0.0)
                Qfr_list.append(0.0)
                q_friction_equivalent.append(0.0)
                #JDR
                D_r.append(0.0) 
                F_Dr.append(0.0)
                F_sig.append(0.0) 
                #JDR
            else:
                plr = plr_list[i]
                qt = qt_list[i]
                depthm = depths[i] #depthm er dybden 
                z_from_toe = this_penetration - depthm
                area_side = pile.perimeter(z_from_toe)
                outer_diameter = pile.outer_diameter(z_from_toe)
                inner_diameter = outer_diameter - 2 * pile.thickness(
                    z_from_toe    
                )
                this_soil_type = layers[i].soil_type
                


                if this_soil_type == 'c':
                    '''
                    f_st = layers[i].prop['f_st']
                    equivalent_diameter = (
                        outer_diameter
                        if closed_pile
                        else (outer_diameter**2 - inner_diameter**2) ** 0.5
                    )
                    q_friction.append(
                        0.07
                        * f_st
                        * qt
                        * max(1, z_from_toe / equivalent_diameter) ** (-0.25)
                    )
                    Qfr_list.append(q_friction[-1] * area_side * dsf_o)
                    '''
                    

                else:
                    
                    #JDR
                    # Friction
                    D_r.append(0.4 * math.log(qt/(22 * math.pow(eff_stress[i]*refpressure, 0.5)))) 
                    F_Dr.append(2.1 * math.pow(D_r[-1]-0.1, 1.7)) 
                    F_sig.append(math.pow(eff_stress[i]/refpressure, 0.25))

                    F_last = 1.3 if compression else 1.0 
                    F_spiss = 1.6 if closed_pile else 1.0
                    # Z_max skal være pelespissens endelige dybde under terreng
                    q_friction.append(max(((depthm/this_penetration)*refpressure*F_Dr[-1] 
                    * F_last * F_spiss * F_sig[-1] * F_mat), 0.1 * eff_stress[i]))

                    #JDR

                q_friction_equivalent.append(Qfr_list[-1] / area_side)
                Qfr_list.append(q_friction[-1] * area_side * dsf_o)

        # Calculate unit toe resistance
        if this_soil_type == 'c':
            ktc = SOIL_COEFF_NGI99[this_soil_type]['toe']['ktc']
            plr = 0.0
            qtip = ktc * qt if eff_stress[i_depth] > 0.0 else 0.0
            qtip *= 2.0 if closed_pile else 1.0
        elif this_soil_type == 's':
            outer_diameter = pile.outer_diameter(0.0)
            thickness = pile.thickness(0.0)
            inner_diameter = outer_diameter - 2 * thickness
            plr = (
                math.tanh(
                    0.3 * ((outer_diameter - 2 * thickness) / 0.0357) ** 0.5
                )
                if not closed_pile
                else 0.0
            )
            area_eff = 1 - plr * (inner_diameter / outer_diameter) ** 2
            #qtip = (0.12 + 0.38 * area_eff) * qp
            qtip = (0.8 * qc/(1+math.pow(D_r[-1], 2))) if closed_pile else min((0.7 * qc/(1+3 * math.pow(D_r[-1], 2))), (qc + 3*q_friction[-1])) # Hva skal være sidefriksjonen her? 
        qtip *= 1.0 if compression else 0.0
        
        plr_list.append(plr)
        
         # Calculate Qtip
        Q_tip.append(qtip * full_area_steel_tip)
                
        Q_friction.append(
            scipy.integrate.trapezoid(Qfr_list, depths[: i_depth + 1])
        )
       

        # Calculate srd best estimate and upper bound
        resistance_best.append(Q_tip[-1] + Q_friction[-1])
        resistance_upper.append(resistance_best[-1] * 1.0)

    # Collect results
    results = {
        'depth': depths,
        'resistance': resistance_best,
        'resistance_upper': resistance_upper,
        'Q_friction': Q_friction,
        'toe_resistance': Q_tip,
        'side_friction': q_friction,
        'side_friction_equivalent_one_face': q_friction_equivalent,
    }

    return results

'''