#ywb002因子 共24个
Alpha_21=((-1*rank((open_0-delay(high_0,1))))*rank((open_0-delay(close_0,1))))*rank((open_0-delay(low_0,1)))
Alpha_2=rank(ts_argmax(signedpower(where(close_0/shift(close_0,1)-1<0,std(close_0/shift(close_0,1)-1<0,20),close_0),2),5))-0.5
Alpha_5=-1*ts_rank(rank(low_0),9)
Alpha_7=-1*correlation(open_0,volume_0,10)
Alpha_18=((-1*rank(ts_rank(close_0,10)))*rank(delta(delta(close_0,1),1)))*rank(ts_rank((volume_0/mean(amount_0,20)),5))
Alpha_19=-1*rank(((std(abs((close_0-open_0)),5)+(close_0-open_0))+correlation(close_0,open_0,10)))
Alpha_23=-1*(delta(correlation(high_0,volume_0,5),5)*rank(std(close_0,20)))
Alpha_26=rank(-1*(close_0/shift(close_0,1)-1)*mean(amount_0,20)*amount_0/volume_0*adjust_factor_0*(high_0-close_0))
Alpha_29=scale(correlation(mean(amount_0,20),low_0,5)+(high_0+low_0)*0.5-close_0)
Alpha_31=((1.0-rank(((sign((close_0-delay(close_0,1)))+sign((delay(close_0,1)-delay(close_0,2))))+sign((delay(close_0,2)-delay(close_0,3))))))*sum(volume_0,5))/sum(volume_0,20)
Alpha_32=(rank(rank(rank(decay_linear((-1*rank(rank(delta(close_0,10)))),10))))+rank((-1*delta(close_0,3))))+sign(scale(correlation(mean(amount_0,20),low_0,12)))
Alpha_41=((-1*rank(std(high_0,10)))*correlation(high_0,volume_0,10))

Alpha_48=(((rank((1/close_0))*volume_0)/mean(amount_0,20))*((high_0*rank((high_0-close_0)))/(sum(high_0,5) /5)))-rank((amount_0/volume_0*adjust_factor_0-delay(amount_0/volume_0*adjust_factor_0,5)))
Alpha_83=(rank(delay(((high_0-low_0)/(sum(close_0,5)/5)),2))*rank(rank(volume_0)))/(((high_0-low_0)/(sum(close_0,5)/5))/(amount_0/volume_0*adjust_factor_0-close_0))
Alpha_43=(rank((amount_0/volume_0*adjust_factor_0-close_0))/rank((amount_0/volume_0*adjust_factor_0+close_0)))
Alpha_34=rank((-1*((1-(open_0/close_0)))))
Alpha_12=(rank(ts_max((amount_0/volume_0*adjust_factor_0-close_0),3))+rank(ts_min((amount_0/volume_0*adjust_factor_0-close_0),3)))*rank(delta(volume_0,3))
Alpha_55=((-1*((low_0-close_0)*(open_0**5)))/((low_0-high_0)*(close_0** 5)))
Alpha_101=(close_0-open_0)/((high_0-low_0)+0.001)
Alpha_17=-1*rank(covariance(rank(high_0),rank(volume_0),5))
Alpha_9=(-1*rank(((sum(open_0,5)*sum(close_0/shift(close_0,1)-1,5))-delay((sum(open_0,5)*sum(close_0/shift(close_0,1)-1,5)),10))))
Alpha_42=(((high_0*low_0)**0.5)-amount_0/volume_0*adjust_factor_0)
Alpha_6=rank((open_0-(sum(amount_0/volume_0*adjust_factor_0,10)/10)))*(-1*abs(rank((close_0-amount_0/volume_0*adjust_factor_0))))
Alpha_57=0-1*(1*(rank((sum(close_0/shift(close_0,1)-1,10)/sum(sum(close_0/shift(close_0,1)-1,2),3)))*rank(((close_0/shift(close_0,1)-1)*market_cap_0))))

#因子权限排序
#32 26 42 48 43 101 23 17 83 2 6 5 19 9 55 32 41 57 7 18 12 31 21 29

#待选择 20内因子 中期
Alpha_56=-1*correlation(rank(((close_0-ts_min(low_0,12))/(ts_max(high_0,12)-ts_min(low_0,12)))),rank(volume_0),6)
Alpha_60=(0-(1*((2*scale(rank(((((close_0-low_0)-(high_0-close_0))/(high_0-low_0))*volume_0))))-scale(rank(ts_argmax(close_0,10))))))
Alpha_62=(rank(correlation(amount_0/volume_0*adjust_factor_0,sum(mean(amount_0,20),22),10))<rank(((rank(open_0)+rank(open_0))<(rank(((high_0+low_0)/2))+rank(high_0)))))*-1
Alpha_68=((ts_rank(correlation(rank(high_0),rank(mean(amount_0,15)),9),14)<rank(delta(((close_0*0.518371)+(low_0*(1-0.518371))),1.06157)))*-1)
Alpha_86=(ts_rank(correlation(close_0,sum(mean(amount_0,20),15),6),20)<rank(((open_0+close_0)-(amount_0/volume_0*adjust_factor_0+open_0))))*-1


#ywb 003 在002基础上增加因子
Alpha_27=-1*ts_max(correlation(ts_rank(volume_0,5),ts_rank(high_0,5),5),3)
Alpha_56=-1*correlation(rank(((close_0-ts_min(low_0,12))/(ts_max(high_0,12)-ts_min(low_0,12)))),rank(volume_0),6)

#ywb 003 在002基础上减少因子
Alpha_21=((-1*rank((open_0-delay(high_0,1))))*rank((open_0-delay(close_0,1))))*rank((open_0-delay(low_0,1)))
Alpha_29=scale(correlation(mean(amount_0,20),low_0,5)+(high_0+low_0)*0.5-close_0)